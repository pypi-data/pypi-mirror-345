"""OpenAI Provider Implementation.

This module implements the LLMAPI interface for OpenAI models.
"""

import logging
import os
from collections.abc import Iterator
from typing import Any, override

import openai
from openai.types import chat

from streetrace.llm.llmapi import LLMAPI
from streetrace.llm.openai.converter import OpenAIHistoryConverter
from streetrace.llm.wrapper import ContentPart, History, Message

# Constants
MAX_TOKENS = 128000  # GPT-4 Turbo has a context window of 128K tokens
MODEL_NAME = "gpt-4-turbo-2024-04-09"  # Default model
MIN_CONVERSATION_LENGTH = 3  # Minimum number of messages before pruning

ProviderHistory = list[chat.ChatCompletionMessageParam]

# Module-level logger
logger = logging.getLogger(__name__)


class OpenAI(LLMAPI):
    """Implementation of the LLMAPI interface for OpenAI models."""

    _adapter: OpenAIHistoryConverter = None

    def __init__(self, adapter: OpenAIHistoryConverter | None = None) -> None:
        """Initialize the OpenAI implementation.

        Args:
            adapter (OpenAIHistoryConverter, optional): Adapter for converting history. Defaults to None.

        """
        super().__init__()
        self._adapter = adapter or OpenAIHistoryConverter()

    @override
    def initialize_client(self) -> openai.OpenAI:
        """Initialize and return the OpenAI API client.

        Returns:
            OpenAI: The initialized OpenAI client

        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set

        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            msg = "OPENAI_API_KEY environment variable not set."
            raise ValueError(msg)

        base_url = os.environ.get("OPENAI_API_BASE")
        if base_url:
            return openai.OpenAI(api_key=api_key, base_url=base_url)
        return openai.OpenAI(api_key=api_key)

    @override
    def transform_history(self, history: History) -> ProviderHistory:
        """Transform conversation history from common format into OpenAI-specific format.

        Args:
            history (History): Conversation history to transform

        Returns:
            List[Dict[str, Any]]: Conversation history in OpenAI-specific format

        """
        return self._adapter.create_provider_history(history)

    def append_history(
        self,
        provider_history: ProviderHistory,
        turn: list[Message],
    ) -> None:
        """Add turn items into provider's conversation history.

        Args:
            provider_history: List of provider-specific message objects
            turn: List of items in this turn

        """
        for message in self._adapter.to_provider_history_items(turn):
            provider_history.append(message)

    @override
    def transform_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform tools from common format to OpenAI-specific format.

        Args:
            tools: List of tool definitions in common format

        Returns:
            List[Dict[str, Any]]: List of tool definitions in OpenAI format

        """
        # OpenAI's tool format is already compatible with the common format
        return tools

    @override
    def pretty_print(self, messages: list[dict[str, Any]]) -> str:
        """Format message list for readable logging.

        Args:
            messages: List of message objects to format

        Returns:
            str: Formatted string representation

        """
        parts = []
        for i, message in enumerate(messages):
            content_str = str(message.get("content", "NONE"))
            role = message.get("role", "unknown")
            parts.append(f"Message {i + 1}:\n - {role}: {content_str}")

        return "\n".join(parts)

    @override
    def manage_conversation_history(
        self,
        conversation_history: list[dict[str, Any]],
        max_tokens: int = MAX_TOKENS,
    ) -> bool:
        """Ensure conversation history is within token limits by intelligently pruning when needed.

        Args:
            conversation_history: List of message objects to manage
            max_tokens: Maximum token limit

        Returns:
            bool: True if successful, False if pruning failed

        """
        result = True
        try:
            # Simplified token count estimation - would need actual token counting in production
            # This is a placeholder for an actual token counting function
            estimated_tokens = sum(len(str(msg)) for msg in conversation_history) // 4

            # If within limits, no action needed
            if estimated_tokens <= max_tokens:
                return True

            logger.info(
                "Estimated token count %s exceeds limit %s, pruning...",
                estimated_tokens,
                max_tokens,
            )

            # Keep first item (usually system message) and last N exchanges
            if len(conversation_history) > MIN_CONVERSATION_LENGTH:
                # Keep important context - first message and recent exchanges
                preserve_count = min(5, len(conversation_history) // 2)
                conversation_history[:] = [
                    conversation_history[0],
                ] + conversation_history[-preserve_count:]

                # Recheck token count
                estimated_tokens = (
                    sum(len(str(msg)) for msg in conversation_history) // 4
                )
                logger.info(
                    "After pruning: %s tokens with %s items",
                    estimated_tokens,
                    len(conversation_history),
                )

                if estimated_tokens <= max_tokens:
                    result = True
                else:
                    # If still exceeding after pruning
                    logger.warning(
                        "Still exceeding token limit after pruning: %s",
                        estimated_tokens,
                    )
                    result = False
            else:
                # If conversation is small but still exceeding, we have a problem
                logger.warning(
                    "Cannot reduce token count sufficiently: %s",
                    estimated_tokens,
                )
                result = False

        except Exception:
            logger.exception("Error managing tokens")
            result = False

        return result

    @override
    def generate(
        self,
        client: openai.OpenAI,
        model_name: str | None,
        system_message: str,
        messages: ProviderHistory,
        tools: list[dict[str, Any]],
    ) -> Iterator[ContentPart]:
        """Get API response from OpenAI, process it and handle tool calls.

        Args:
            client: The OpenAI client
            model_name: The model name to use
            system_message: Not used in OpenAI (processed as a part of conversation history)
            messages: The messages to send in the request
            tools: The tools to use

        Returns:
            Iterator[ContentPart]: Stream of response parts

        """
        # UNRESOLVED ISSUE with streaming is that
        # when printing to console, we need to re-draw the full content accumulated so far
        # to render mardown output, which would require a significant upgrate on the UI.
        # Between streaming and markdown, I choose markdown.
        model_name = model_name or MODEL_NAME

        logger.debug("Sending request: %s", messages)
        # Create the message with OpenAI
        response: chat.ChatCompletion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            stream=False,
            tool_choice="auto",
        )
        logger.debug("Response received: %s", response)

        if not isinstance(response, chat.ChatCompletion) or not hasattr(
            response,
            "choices",
        ):
            msg = f"Invalid response from OpenAI API: {response}"
            raise ValueError(msg)

        return self._adapter.get_response_parts(response)
