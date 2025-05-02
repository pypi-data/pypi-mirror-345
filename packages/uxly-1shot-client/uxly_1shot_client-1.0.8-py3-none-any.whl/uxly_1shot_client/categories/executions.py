"""Executions module for the 1Shot API."""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.execution import TransactionExecution


class ExecutionListParams(BaseModel):
    """Parameters for listing executions."""

    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")
    chain_id: Optional[int] = Field(None, alias="chainId", description="The specific chain to get the executions for")
    status: Optional[str] = Field(None, description="The status of the executions to return")
    escrow_wallet_id: Optional[str] = Field(None, alias="escrowWalletId", description="The escrow wallet ID to get the executions for")
    transaction_id: Optional[str] = Field(None, alias="transactionId", description="The transaction ID to get the executions for")
    api_credential_id: Optional[str] = Field(None, alias="apiCredentialId", description="The API credential ID to get the executions for")
    user_id: Optional[str] = Field(None, alias="userId", description="The user ID to get the executions for")

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


class Executions:
    """Executions module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the executions module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_list_url(self, business_id: str) -> str:
        """Get the URL for listing executions.

        Args:
            business_id: The business ID

        Returns:
            The URL for listing executions
        """
        return f"/business/{business_id}/executions"

    def _get_get_url(self, execution_id: str) -> str:
        """Get the URL for getting an execution.

        Args:
            execution_id: The execution ID

        Returns:
            The URL for getting an execution
        """
        return f"/executions/{execution_id}"


class SyncExecutions(Executions):
    """Synchronous executions module for the 1Shot API."""

    def list(
        self, business_id: str, params: Optional[ExecutionListParams] = None
    ) -> PagedResponse[TransactionExecution]:
        """List executions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of executions
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = self._client._request("GET", url, params=query_params)
        else:
            response = self._client._request("GET", url)
        return PagedResponse[TransactionExecution].model_validate(response)

    def get(self, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            execution_id: The execution ID

        Returns:
            The execution
        """
        url = self._get_get_url(execution_id)
        response = self._client._request("GET", url)
        return TransactionExecution.model_validate(response)


class AsyncExecutions(Executions):
    """Asynchronous executions module for the 1Shot API."""

    async def list(
        self, business_id: str, params: Optional[ExecutionListParams] = None
    ) -> PagedResponse[TransactionExecution]:
        """List executions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of executions
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = await self._client._request("GET", url, params=query_params)
        else:
            response = await self._client._request("GET", url)
        return PagedResponse[TransactionExecution].model_validate(response)

    async def get(self, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            execution_id: The execution ID

        Returns:
            The execution
        """
        url = self._get_get_url(execution_id)
        response = await self._client._request("GET", url)
        return TransactionExecution.model_validate(response)