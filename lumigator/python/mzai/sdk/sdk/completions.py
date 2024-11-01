"""Completions SDK

Provides a class to perform LLM vendor-based API inference from within in Lumigator.
"""

import json
from http import HTTPMethod, HTTPStatus

from schemas.completions import CompletionResponse

from sdk.client import ApiClient


class Completions:
    COMPLETIONS_ROUTE = "completions"

    def __init__(self, c: ApiClient):
        self.__client = c
        self.__cached_vendors = self.get_vendors()

    def get_vendors(self) -> list[str]:
        """Returns the list of supported external vendors."""
        response = self.__client.get_response(self.COMPLETIONS_ROUTE)

        if not response:
            return []

        # Update the cached vendors.
        self.__cached_vendors = [str(vendor).lower() for vendor in response.json()]

        return self.__cached_vendors

    def get_completion(self, vendor: str, text: str) -> CompletionResponse | None:
        """Returns completions from the specified vendor for given text (prompt)."""
        # Sanitize the inputs.
        vendor = vendor.lower()
        text = text.strip()

        # Attempt to validate vendors using the cache.
        if vendor not in self.__cached_vendors:
            raise ValueError(
                f"vendor: '{vendor}' was not found in cache, 'get_vendors' to update cache)"
            )

        # Validate we have some text input as our prompt.
        if text == "":
            raise ValueError("text: cannot be empty or whitespace")

        endpoint = f"{self.COMPLETIONS_ROUTE}/{vendor}/"
        response = self.__client.get_response(
            endpoint, HTTPMethod.POST, json_data=json.dumps(f'{{"text":"{text}"}}')
        )

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return CompletionResponse(**data)
