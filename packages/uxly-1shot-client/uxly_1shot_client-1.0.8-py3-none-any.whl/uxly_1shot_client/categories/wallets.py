"""Wallets module for the 1Shot API."""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.wallet import EscrowWallet


class WalletListParams(BaseModel):
    """Parameters for listing wallets."""

    chain_id: Optional[int] = Field(None, alias="chainId", description="The specific chain to get the wallets for")
    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")

    @validator('page')
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page number must be greater than or equal to 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page size must be greater than or equal to 1')
        return v


class WalletCreateParams(BaseModel):
    """Parameters for creating a wallet."""

    chain: int = Field(..., description="The chain ID to create the wallet on")
    name: str = Field(..., description="The name of the escrow wallet")
    description: Optional[str] = Field(None, description="A description of the escrow wallet, such as it's intended use. This is for reference only.")


class WalletUpdateParams(BaseModel):
    """Parameters for updating a wallet."""

    name: Optional[str] = Field(None, description="The name of the escrow wallet")
    description: Optional[str] = Field(None, description="Optional description of the escrow wallet, can be used to describe it's purpose")


class Wallets:
    """Wallets module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the wallets module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_list_url(self, business_id: str) -> str:
        """Get the URL for listing wallets.

        Args:
            business_id: The business ID

        Returns:
            The URL for listing wallets
        """
        return f"/business/{business_id}/wallets"

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a wallet.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a wallet
        """
        return f"/business/{business_id}/wallets"

    def _get_get_url(self, escrow_wallet_id: str) -> str:
        """Get the URL for getting a wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            The URL for getting a wallet
        """
        return f"/wallets/{escrow_wallet_id}"

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
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = self._client._request("GET", url, params=query_params)
        else:
            response = self._client._request("GET", url)
        return PagedResponse[EscrowWallet].model_validate(response)

    def create(self, business_id: str, params: WalletCreateParams) -> EscrowWallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the wallet

        Returns:
            The created wallet
        """
        url = self._get_create_url(business_id)
        response = self._client._request("POST", url, json=params.dict(exclude_none=True))
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
        """
        url = self._get_get_url(escrow_wallet_id)
        params = {"includeBalances": str(include_balances).lower()} if include_balances is not None else None
        response = self._client._request("GET", url, params=params)
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
        """
        url = self._get_update_url(escrow_wallet_id)
        response = self._client._request("PUT", url, json=params.dict(exclude_none=True))
        return EscrowWallet.model_validate(response)

    def delete(self, escrow_wallet_id: str) -> Dict[str, bool]:
        """Delete an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            A dictionary with a success flag
        """
        url = self._get_delete_url(escrow_wallet_id)
        return self._client._request("DELETE", url)


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
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = await self._client._request("GET", url, params=query_params)
        else:
            response = await self._client._request("GET", url)
        return PagedResponse[EscrowWallet].model_validate(response)

    async def create(self, business_id: str, params: WalletCreateParams) -> EscrowWallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the wallet

        Returns:
            The created wallet
        """
        url = self._get_create_url(business_id)
        response = await self._client._request("POST", url, json=params.dict(exclude_none=True))
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
        """
        url = self._get_get_url(escrow_wallet_id)
        params = {"includeBalances": str(include_balances).lower()} if include_balances is not None else None
        response = await self._client._request("GET", url, params=params)
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
        """
        url = self._get_update_url(escrow_wallet_id)
        response = await self._client._request("PUT", url, json=params.dict(exclude_none=True))
        return EscrowWallet.model_validate(response)

    async def delete(self, escrow_wallet_id: str) -> Dict[str, bool]:
        """Delete an escrow wallet.

        Args:
            escrow_wallet_id: The wallet ID

        Returns:
            A dictionary with a success flag
        """
        url = self._get_delete_url(escrow_wallet_id)
        return await self._client._request("DELETE", url) 