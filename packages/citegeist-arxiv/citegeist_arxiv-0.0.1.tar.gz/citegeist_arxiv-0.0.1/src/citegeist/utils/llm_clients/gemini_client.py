"""
Gemini API client implementation.
"""

import requests

from .base_client import LLMClient, exponential_backoff_retry


class GeminiClient(LLMClient):
    """Client for Gemini API."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initializes the Gemini client.

        Args:
            model_name (str): The model name.
            api_key (str): The API key.
        """
        self.api_key = api_key
        self.model_name = model_name

    def get_completion(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.0, **kwargs) -> str:
        """
        Wraps prompt in a contents object, which is passed to get_chat_completions.

        Args:
            prompt (str): The prompt.
            max_tokens (int): The maximum number of tokens to return.
            temperature (float): The temperature to use.

        Returns:
            The completion.
        """
        contents = [{"parts": [{"text": prompt}]}]
        return self.get_chat_completion(contents, max_tokens, temperature, **kwargs)

    def get_chat_completion(
        self, contents: list[dict[str, list[dict]]], max_tokens: int = 4096, temperature: float = 0.0, **kwargs
    ) -> str:
        """
        Gets chat completions from Gemini API based on the provided contents.

        Args:
            contents: The contents to get chat completions from.
            max_tokens (int): The maximum number of tokens to return.
            temperature (float): The temperature to use.

        Returns:
            The chat completion.
        """

        def call_model() -> str:
            headers = {"Content-Type": "application/json"}

            payload = {
                "contents": contents,
                "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens, **kwargs},
            }

            request_url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}"
                f":generateContent?key={self.api_key}"
            )

            response = requests.post(url=request_url, headers=headers, json=payload)
            response.raise_for_status()
            reply = response.json()

            return reply["candidates"][0]["content"]["parts"][0]["text"]

        return exponential_backoff_retry(call_model)
