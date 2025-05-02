"""Executions module for the 1Shot API."""

from typing import Optional, Union
from enum import IntEnum

from pydantic import BaseModel, Field, validator

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.execution import TransactionExecution
from uxly_1shot_client.base import BaseClient


class ETransactionExecutionStatus(IntEnum):
    """Valid transaction execution status values."""
    PENDING = 0
    SUBMITTED = 1
    COMPLETED = 2
    RETRYING = 3
    FAILED = 4


class ExecutionListParams(BaseModel):
    """Parameters for listing executions."""

    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")
    chain_id: Optional[int] = Field(None, alias="chainId", description="Filter by chain ID")
    status: Optional[ETransactionExecutionStatus] = Field(
        None,
        description="Filter by status (0=Submitted, 1=Completed, 2=Retrying, 3=Failed)",
    )
    escrow_wallet_id: Optional[str] = Field(None, alias="escrowWalletId", description="Filter by escrow wallet ID")
    transaction_id: Optional[str] = Field(None, alias="transactionId", description="Filter by transaction ID")
    api_credential_id: Optional[str] = Field(None, alias="apiCredentialId", description="Filter by API credential ID")
    user_id: Optional[str] = Field(None, alias="userId", description="Filter by user ID")

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


class Executions(BaseClient):
    """Executions module for the 1Shot API."""

    def _get_list_url(self, business_id: str) -> str:
        """Get the URL for listing executions.

        Args:
            business_id: The business ID

        Returns:
            The URL for listing executions
        """
        return f"{self.base_url}/business/{business_id}/transactions/executions"

    def _get_get_url(self, transaction_id: str, execution_id: str) -> str:
        """Get the URL for getting an execution.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The URL for getting an execution
        """
        return f"{self.base_url}/transactions/{transaction_id}/executions/{execution_id}"

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
            response = self._request("GET", url, params=query_params)
        else:
            response = self._request("GET", url)
        return PagedResponse[TransactionExecution].model_validate(response)

    def get(self, transaction_id: str, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The execution
        """
        url = self._get_get_url(transaction_id, execution_id)
        response = self._request("GET", url)
        return TransactionExecution.model_validate(response)


class AsyncExecutions(BaseClient):
    """Asynchronous executions module for the 1Shot API."""

    def _get_list_url(self, business_id: str) -> str:
        """Get the URL for listing executions.

        Args:
            business_id: The business ID

        Returns:
            The URL for listing executions
        """
        return f"{self.base_url}/business/{business_id}/transactions/executions"

    def _get_get_url(self, transaction_id: str, execution_id: str) -> str:
        """Get the URL for getting an execution.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The URL for getting an execution
        """
        return f"{self.base_url}/transactions/{transaction_id}/executions/{execution_id}"

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
            response = await self._request("GET", url, params=query_params)
        else:
            response = await self._request("GET", url)
        return PagedResponse[TransactionExecution].model_validate(response)

    async def get(self, transaction_id: str, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The execution
        """
        url = self._get_get_url(transaction_id, execution_id)
        response = await self._request("GET", url)
        return TransactionExecution.model_validate(response)