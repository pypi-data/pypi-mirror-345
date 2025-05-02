"""Ollama Provider Implementation.

This module implements the LLMAPI interface for Ollama models.
"""

import logging
import os
from collections.abc import Iterator
from typing import Any, override

import ollama

from streetrace.llm.llmapi import LLMAPI
from streetrace.llm.ollama.converter import OllamaHistoryConverter
from streetrace.llm.wrapper import ContentPart, History, Message

# Constants
MAX_TOKENS = 32768
"Default context window for most Ollama models."
MODEL_NAME = "llama3.1:8b"
"Default model."
MIN_MESSAGES_FOR_PRUNING = 3
"Minimum number of messages before pruning."
MAX_PRESERVE_COUNT = 5
"Maximum number of messages to preserve during pruning."

# Module-level logger
logger = logging.getLogger(__name__)

ProviderHistory = list[dict[str, Any]]


class Ollama(LLMAPI):
    """Implementation of the LLMAPI interface for Ollama models."""

    _adapter: OllamaHistoryConverter

    def __init__(self, adapter: OllamaHistoryConverter | None = None) -> None:
        """Initialize the Ollama implementation.

        Args:
            adapter (OllamaHistoryConverter, optional): Adapter for converting history. Defaults to None.

        """
        super().__init__()
        self._adapter = adapter or OllamaHistoryConverter()

    @override
    def initialize_client(self) -> ollama.Client:
        """Initialize and return the Ollama API client.

        Returns:
            ollama.Client: The initialized Ollama client

        """
        host = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
        return ollama.Client(host=host)

    @override
    def transform_history(self, history: History) -> ProviderHistory:
        """Transform conversation history from common format into Ollama-specific format.

        Args:
            history (History): Conversation history to transform

        Returns:
            List[Dict[str, Any]]: Conversation history in Ollama-specific format

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
        """Transform tools from common format to Ollama-specific format.

        Args:
            tools: List of tool definitions in common format

        Returns:
            List[Dict[str, Any]]: List of tool definitions in Ollama format

        """
        # Ollama generally uses the same tool format as OpenAI, so no transformation is needed
        return tools

    @override
    def pretty_print(self, messages: ProviderHistory) -> str:
        """Format message list for readable logging.

        Args:
            messages: List of message objects to format

        Returns:
            str: Formatted string representation

        """
        parts = []
        for i, message in enumerate(messages):
            content_str = str(
                message.get("content", message.get("function", {}).get("name", "NONE")),
            )
            role = message.get("role", "unknown")
            parts.append(f"Message {i + 1}:\n - {role}: {content_str}")

        return "\n".join(parts)

    @override
    def manage_conversation_history(
        self,
        messages: ProviderHistory,
        max_tokens: int = MAX_TOKENS,
    ) -> bool:
        """Ensure conversation history is within token limits by intelligently pruning when needed.

        Args:
            messages: List of message objects to manage
            max_tokens: Maximum token limit

        Returns:
            bool: True if successful, False if pruning failed

        """
        result = False

        try:
            # Simplified token count estimation - would need actual token counting in production
            estimated_tokens = sum(len(str(msg)) for msg in messages) // 4

            # If within limits, no action needed
            if estimated_tokens <= max_tokens:
                return True

            logger.info(
                "Estimated token count %s exceeds limit %s, pruning...",
                estimated_tokens,
                max_tokens,
            )

            # Keep first item (usually system message) and last N exchanges
            if len(messages) > MIN_MESSAGES_FOR_PRUNING:
                # Keep important context - first message and recent exchanges
                preserve_count = min(MAX_PRESERVE_COUNT, len(messages) // 2)
                messages[:] = [messages[0]] + messages[-preserve_count:]

                # Recheck token count
                estimated_tokens = sum(len(str(msg)) for msg in messages) // 4
                logger.info(
                    "After pruning: %s tokens with %s items",
                    estimated_tokens,
                    len(messages),
                )

                result = estimated_tokens <= max_tokens
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
        client: ollama.Client,
        model_name: str | None,
        system_message: str,
        messages: ProviderHistory,
        tools: list[dict[str, Any]],
    ) -> Iterator[ContentPart]:
        """Get API response from Ollama, process it and handle tool calls.

        Args:
            client: The Ollama client
            model_name: The model name to use
            system_message: The system message to use (already included in messages)
            messages: The messages to send in the request
            tools: The tools to use in Ollama format

        Returns:
            Iterator[ContentPart]: Stream of response parts

        """
        model_name = model_name or MODEL_NAME
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:  # This loop handles retries for errors
            try:
                # Create the message with Ollama
                response = client.chat(
                    model=model_name,
                    messages=messages,
                    tools=tools,
                    stream=False,
                )

                if isinstance(response, ollama.ChatResponse):
                    yield from self._adapter.get_response_parts(response)
                else:
                    for message in response:
                        yield from self._adapter.get_response_parts(message)

                break  # Exit loop if successful

            except Exception as e:
                retry_count += 1

                if retry_count >= max_retries:
                    error_msg = f"Failed after {max_retries} retries: {e}"
                    logger.exception(error_msg)
                    raise
                else:
                    error_msg = f"API error encountered. Retrying... (Attempt {retry_count}/{max_retries}): {e}"
                    logger.warning(error_msg)
