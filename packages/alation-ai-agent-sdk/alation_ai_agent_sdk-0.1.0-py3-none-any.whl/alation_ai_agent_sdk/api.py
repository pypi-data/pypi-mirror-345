import logging
import time
import urllib.parse
import json
from typing import Dict, Any, Optional
from http import HTTPStatus
import requests


class AlationAPIError(Exception):
    pass


class AlationAPI:
    """
    Client for interacting with the Alation API.

    This class manages authentication and provides methods to retrieve
    context-specific information from the Alation catalog.

    Attributes:
        base_url (str): Base URL for the Alation instance
        user_id (int): Numeric ID of the Alation user
        refresh_token (str): Refresh token for API authentication
        access_token (str, optional): Current API access token
        token_expiry (int): Timestamp for token expiration (Unix timestamp)
    """
    def __init__(self, base_url: str, user_id: int, refresh_token: str):
        self.base_url = base_url
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = 0  # Unix timestamp

    def _is_token_valid(self) -> bool:
        """
        Check if the current token is still valid with a safety buffer.

        Returns:
            bool: True if the token is valid, False otherwise
        """
        return (self.access_token is not None and
                time.time() < self.token_expiry)

    def _generate_access_token(self):
        """
        Generate a new access token for API authentication.
        """

        # Skip token generation if the current token is still valid
        if self._is_token_valid():
            return

        url = f"{self.base_url}/integration/v1/createAPIAccessToken/"
        payload = {
            "user_id": self.user_id,
            "refresh_token": self.refresh_token,
        }

        response = requests.post(url, json=payload, timeout=30)

        # Accept both 200 (OK) and 201 (Created)
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            data = response.json()
            self.access_token = data["api_access_token"]
            self.token_expiry = time.time() + 60 * 60  # expires in 1 hour
        else:
            logging.error("Failed to generate access token: %s - %s", response.status_code, response.text)
            api_error_message = "Failed to generate access token"
            raise AlationAPIError(api_error_message)

    def get_context_from_catalog(self, query: str, signature: Optional[Dict[str, Any]] = None):
        """
        Retrieve contextual information from the Alation catalog based on a natural language query and signature.
        """

        if not query:
            raise ValueError("Query cannot be empty")

        self._generate_access_token()
        headers = {
            "Token": self.access_token,  # OR use Authorization if required
        }

        params = {
            "question": query
        }
        # If a signature is provided, include it in the request
        if signature:
            params["signature"] = json.dumps(signature, separators=(",", ":"))

        # URL encode the parameters
        encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        # Construct the full URL with query parameters
        url = f"{self.base_url}/integration/v2/context/?{encoded_params}"

        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code == HTTPStatus.OK:
            return response.json()

        logging.error("Catalog search failed: %s - %s", response.status_code, response.text)
        api_error_message = "Catalog search failed"
        raise AlationAPIError(api_error_message)
