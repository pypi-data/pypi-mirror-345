"""Asynchronous client for the 1Shot API."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Generic

import httpx

from uxly_1shot_client.base import BaseClient, TokenResponse
from uxly_1shot_client.executions import AsyncExecutions
from uxly_1shot_client.structs import AsyncStructs
from uxly_1shot_client.transactions import AsyncTransactions
from uxly_1shot_client.wallets import AsyncWallets

T = TypeVar("T")


class AsyncClient(BaseClient):
    """Asynchronous client for the 1Shot API."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.1shotapi.com/v0",
    ) -> None:
        """Initialize the client.

        Args:
            api_key: Your API key
            api_secret: Your API secret
            base_url: Base URL for the API
        """
        super().__init__(api_key, api_secret, base_url)
        self.executions = AsyncExecutions(self)
        self.transactions = AsyncTransactions(self)
        self.wallets = AsyncWallets(self)
        self.structs = AsyncStructs(self)

    async def __aenter__(self) -> "AsyncClient":
        """Enter the async context.

        Returns:
            The client instance
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context."""
        await self._client.aclose()

    async def _get_access_token(self) -> str:
        """Get an access token.

        Returns:
            The access token

        Raises:
            httpx.HTTPError: If the request fails
        """
        if (
            self._access_token
            and self._token_expiry
            and self._token_expiry > datetime.now()
        ):
            return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_token_url(),
                data=self._get_token_data(),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

            token_data = TokenResponse.model_validate(response.json())
            self._access_token = token_data.access_token
            self._token_expiry = datetime.now() + timedelta(seconds=token_data.expires_in)
            return self._access_token

    async def _request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the API.

        Args:
            method: The HTTP method
            path: The API path
            data: The request data

        Returns:
            The response data

        Raises:
            httpx.HTTPError: If the request fails
        """
        token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                self._get_url(path),
                headers=self._get_headers(),
                json=data,
            )
            response.raise_for_status()
            return response.json() 