"""Executions module for the 1Shot API."""

from typing import Optional, Union

from pydantic import BaseModel, Field

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.execution import TransactionExecution


class ExecutionListParams(BaseModel):
    """Parameters for listing executions."""

    page_size: Optional[int] = Field(None, description="Number of items per page")
    page: Optional[int] = Field(None, description="Page number (1-indexed)")
    chain_id: Optional[int] = Field(None, description="Filter by chain ID")
    status: Optional[int] = Field(
        None,
        description="Filter by status (0=Submitted, 1=Completed, 2=Retrying, 3=Failed)",
    )
    escrow_wallet_id: Optional[str] = Field(None, description="Filter by escrow wallet ID")
    transaction_id: Optional[str] = Field(None, description="Filter by transaction ID")
    api_credential_id: Optional[str] = Field(None, description="Filter by API credential ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")


class Executions:
    """Executions module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the executions module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_list_url(self, business_id: str, params: Optional[ExecutionListParams] = None) -> str:
        """Get the URL for listing executions.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing executions
        """
        url = f"/business/{business_id}/transactions/executions"
        if params:
            query_params = []
            for key, value in params.model_dump(exclude_none=True).items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_get_url(self, transaction_id: str, execution_id: str) -> str:
        """Get the URL for getting an execution.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The URL for getting an execution
        """
        return f"/transactions/{transaction_id}/executions/{execution_id}"


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

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[TransactionExecution].model_validate(response)

    def get(self, transaction_id: str, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The execution

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "GET",
            self._get_get_url(transaction_id, execution_id),
        )
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

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[TransactionExecution].model_validate(response)

    async def get(self, transaction_id: str, execution_id: str) -> TransactionExecution:
        """Get an execution by ID.

        Args:
            transaction_id: The transaction ID
            execution_id: The execution ID

        Returns:
            The execution

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "GET",
            self._get_get_url(transaction_id, execution_id),
        )
        return TransactionExecution.model_validate(response)