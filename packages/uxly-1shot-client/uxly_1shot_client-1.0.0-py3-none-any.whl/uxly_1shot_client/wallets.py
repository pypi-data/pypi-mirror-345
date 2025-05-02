"""Wallets module for the 1Shot API."""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.wallet import EscrowWallet


class WalletListParams(BaseModel):
    """Parameters for listing wallets."""

    chain_id: Optional[int] = Field(None, description="Filter by chain ID")
    page_size: Optional[int] = Field(None, description="Number of items per page")
    page: Optional[int] = Field(None, description="Page number (1-indexed)")


class WalletUpdateParams(BaseModel):
    """Parameters for updating a wallet."""

    name: Optional[str] = Field(None, description="The wallet name")
    description: Optional[str] = Field(None, description="The wallet description")


class Wallets:
    """Wallets module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the wallets module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_list_url(self, business_id: str, params: Optional[WalletListParams] = None) -> str:
        """Get the URL for listing wallets.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing wallets
        """
        url = f"/business/{business_id}/wallets"
        if params:
            query_params = []
            for key, value in params.model_dump(exclude_none=True).items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a wallet.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a wallet
        """
        return f"/business/{business_id}/wallets"

    def _get_get_url(self, escrow_wallet_id: str, include_balances: Optional[bool] = None) -> str:
        """Get the URL for getting a wallet.

        Args:
            escrow_wallet_id: The wallet ID
            include_balances: Whether to include balance information

        Returns:
            The URL for getting a wallet
        """
        url = f"/wallets/{escrow_wallet_id}"
        if include_balances is not None:
            url += f"?includeBalances={str(include_balances).lower()}"
        return url

    def _get_update_url(self, escrow_wallet_id: str) -> str:
        """Get the URL for updating a wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            The URL for updating a wallet
        """
        return f"/wallets/{escrow_wallet_id}"

    def _get_delete_url(self, escrow_wallet_id: str) -> str:
        """Get the URL for deleting a wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            The URL for deleting a wallet
        """
        return f"/wallets/{escrow_wallet_id}"


class SyncWallets(Wallets):
    """Synchronous wallets module for the 1Shot API."""

    def list(
        self, business_id: str, params: Optional[WalletListParams] = None
    ) -> PagedResponse[EscrowWallet]:
        """List escrow wallets for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of wallets

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[EscrowWallet].model_validate(response)

    def create(self, business_id: str, chain: int) -> EscrowWallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            chain: The chain ID

        Returns:
            The created wallet

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "POST",
            self._get_create_url(business_id),
            data={"chain": chain},
        )
        return EscrowWallet.model_validate(response)

    def get(
        self, escrow_wallet_id: str, include_balances: Optional[bool] = None
    ) -> EscrowWallet:
        """Get an escrow wallet by ID.

        Args:
            escrow_wallet_id: The wallet ID
            include_balances: Whether to include balance information

        Returns:
            The wallet

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "GET",
            self._get_get_url(escrow_wallet_id, include_balances),
        )
        return EscrowWallet.model_validate(response)

    def update(
        self, escrow_wallet_id: str, params: WalletUpdateParams
    ) -> EscrowWallet:
        """Update an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID
            params: Update parameters

        Returns:
            The updated wallet

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "PUT",
            self._get_update_url(escrow_wallet_id),
            data=params.model_dump(exclude_none=True),
        )
        return EscrowWallet.model_validate(response)

    def delete(self, escrow_wallet_id: str) -> Dict[str, bool]:
        """Delete an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            A dictionary with a success flag

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._client.request(
            "DELETE",
            self._get_delete_url(escrow_wallet_id),
        )


class AsyncWallets(Wallets):
    """Asynchronous wallets module for the 1Shot API."""

    async def list(
        self, business_id: str, params: Optional[WalletListParams] = None
    ) -> PagedResponse[EscrowWallet]:
        """List escrow wallets for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of wallets

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[EscrowWallet].model_validate(response)

    async def create(self, business_id: str, chain: int) -> EscrowWallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            chain: The chain ID

        Returns:
            The created wallet

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "POST",
            self._get_create_url(business_id),
            data={"chain": chain},
        )
        return EscrowWallet.model_validate(response)

    async def get(
        self, escrow_wallet_id: str, include_balances: Optional[bool] = None
    ) -> EscrowWallet:
        """Get an escrow wallet by ID.

        Args:
            escrow_wallet_id: The wallet ID
            include_balances: Whether to include balance information

        Returns:
            The wallet

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "GET",
            self._get_get_url(escrow_wallet_id, include_balances),
        )
        return EscrowWallet.model_validate(response)

    async def update(
        self, escrow_wallet_id: str, params: WalletUpdateParams
    ) -> EscrowWallet:
        """Update an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID
            params: Update parameters

        Returns:
            The updated wallet

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "PUT",
            self._get_update_url(escrow_wallet_id),
            data=params.model_dump(exclude_none=True),
        )
        return EscrowWallet.model_validate(response)

    async def delete(self, escrow_wallet_id: str) -> Dict[str, bool]:
        """Delete an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            A dictionary with a success flag

        Raises:
            httpx.HTTPError: If the request fails
        """
        return await self._client.request(
            "DELETE",
            self._get_delete_url(escrow_wallet_id),
        ) 