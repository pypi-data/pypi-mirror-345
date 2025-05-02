"""Transactions module for the 1Shot API."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.execution import TransactionExecution
from uxly_1shot_client.models.transaction import (
    TransactionExecution,
    TransactionParams,
    TransactionEstimate,
    TransactionTestResult,
    Transaction,
)
from uxly_1shot_client.base import BaseClient


class Transactions:
    """Transactions module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the transactions module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_test_url(self, transaction_id: str) -> str:
        """Get the URL for testing a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for testing a transaction
        """
        return f"/transactions/{transaction_id}/test"

    def _get_estimate_url(self, transaction_id: str) -> str:
        """Get the URL for estimating a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for estimating a transaction
        """
        return f"/transactions/{transaction_id}/estimate"

    def _get_execute_url(self, transaction_id: str) -> str:
        """Get the URL for executing a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for executing a transaction
        """
        return f"/transactions/{transaction_id}/execute"

    def _get_read_url(self, transaction_id: str) -> str:
        """Get the URL for reading a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for reading a transaction
        """
        return f"/transactions/{transaction_id}/read"

    def _get_get_url(self, transaction_id: str) -> str:
        """Get the URL for getting a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for getting a transaction
        """
        return f"/transactions/{transaction_id}"

    def _get_list_url(self, business_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for listing transactions.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing transactions
        """
        url = f"/business/{business_id}/transactions"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a transaction.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a transaction
        """
        return f"/business/{business_id}/transactions"

    def _get_import_from_abi_url(self, business_id: str) -> str:
        """Get the URL for importing transactions from an ABI.

        Args:
            business_id: The business ID

        Returns:
            The URL for importing transactions from an ABI
        """
        return f"/business/{business_id}/transactions/abi"

    def _get_update_url(self, transaction_id: str) -> str:
        """Get the URL for updating a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for updating a transaction
        """
        return f"/transactions/{transaction_id}"

    def _get_delete_url(self, transaction_id: str) -> str:
        """Get the URL for deleting a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for deleting a transaction
        """
        return f"/transactions/{transaction_id}"

    def _get_restore_url(self, transaction_id: str) -> str:
        """Get the URL for restoring a transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for restoring a transaction
        """
        return f"/transactions/{transaction_id}/restore"


class SyncTransactions(Transactions):
    """Synchronous transactions module for the 1Shot API."""

    def test(self, transaction_id: str, params: TransactionParams) -> TransactionTestResult:
        """Test a transaction execution.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The test result

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_test_url(transaction_id),
            data={"params": params.validate_params()},
        )
        return TransactionTestResult.model_validate(response)

    def estimate(self, transaction_id: str, params: TransactionParams) -> TransactionEstimate:
        """Estimate the cost of executing a transaction.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The cost estimate

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_estimate_url(transaction_id),
            data={"params": params.validate_params()},
        )
        return TransactionEstimate.model_validate(response)

    def execute(
        self,
        transaction_id: str,
        params: TransactionParams,
        escrow_wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> TransactionExecution:
        """Execute a transaction.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction
            escrow_wallet_id: Optional ID of the escrow wallet to use
            memo: Optional memo for the execution

        Returns:
            The execution result

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data = {"params": params.validate_params()}
        if escrow_wallet_id is not None:
            data["escrow_wallet_id"] = escrow_wallet_id
        if memo is not None:
            data["memo"] = memo

        response = self._client._request(
            "POST",
            self._get_execute_url(transaction_id),
            data=data,
        )
        return TransactionExecution.model_validate(response)

    def read(self, transaction_id: str, params: TransactionParams) -> Dict[str, Any]:
        """Read the result of a view/pure function.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The function result

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._client._request(
            "POST",
            self._get_read_url(transaction_id),
            data={"params": params.validate_params()},
        )

    def get(self, transaction_id: str) -> Transaction:
        """Get a transaction by ID.

        Args:
            transaction_id: The transaction ID

        Returns:
            The transaction

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "GET",
            self._get_get_url(transaction_id),
        )
        return Transaction.model_validate(response)

    def list(
        self,
        business_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PagedResponse[Transaction]:
        """List transactions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of transactions

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[Transaction].model_validate(response)

    def create(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> Transaction:
        """Create a new transaction.

        Args:
            business_id: The business ID
            params: Transaction creation parameters

        Returns:
            The created transaction

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_create_url(business_id),
            data=params,
        )
        return Transaction.model_validate(response)

    def import_from_abi(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> List[TransactionExecution]:
        """Import transactions from an ABI.

        Args:
            business_id: The business ID
            params: ABI import parameters

        Returns:
            The imported transactions

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_import_from_abi_url(business_id),
            data=params,
        )
        return [TransactionExecution.model_validate(tx) for tx in response]

    def update(
        self,
        transaction_id: str,
        params: Dict[str, Any],
    ) -> Transaction:
        """Update a transaction.

        Args:
            transaction_id: The transaction ID
            params: Update parameters

        Returns:
            The updated transaction

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "PUT",
            self._get_update_url(transaction_id),
            data=params,
        )
        return Transaction.model_validate(response)

    def delete(self, transaction_id: str) -> None:
        """Delete a transaction.

        Args:
            transaction_id: The transaction ID

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._client._request(
            "DELETE",
            self._get_delete_url(transaction_id),
        )

    def restore(self, transaction_id: str) -> List[Transaction]:
        """Restore a deleted transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The restored transactions

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "PUT",
            self._get_restore_url(transaction_id),
            data={"rewardIds": [transaction_id]},
        )
        return [Transaction.model_validate(tx) for tx in response]


class AsyncTransactions(Transactions):
    """Asynchronous transactions module for the 1Shot API."""

    async def test(self, transaction_id: str, params: TransactionParams) -> TransactionTestResult:
        """Test a transaction execution.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The test result

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_test_url(transaction_id),
            data={"params": params.validate_params()},
        )
        return TransactionTestResult.model_validate(response)

    async def estimate(self, transaction_id: str, params: TransactionParams) -> TransactionEstimate:
        """Estimate the cost of executing a transaction.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The cost estimate

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_estimate_url(transaction_id),
            data={"params": params.validate_params()},
        )
        return TransactionEstimate.model_validate(response)

    async def execute(
        self,
        transaction_id: str,
        params: TransactionParams,
        escrow_wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> TransactionExecution:
        """Execute a transaction.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction
            escrow_wallet_id: Optional ID of the escrow wallet to use
            memo: Optional memo for the execution

        Returns:
            The execution result

        Raises:
            httpx.HTTPError: If the request fails
        """
        data = {"params": params.validate_params()}
        if escrow_wallet_id is not None:
            data["escrow_wallet_id"] = escrow_wallet_id
        if memo is not None:
            data["memo"] = memo

        response = await self._client._request(
            "POST",
            self._get_execute_url(transaction_id),
            data=data,
        )
        return TransactionExecution.model_validate(response)

    async def read(self, transaction_id: str, params: TransactionParams) -> Dict[str, Any]:
        """Read the result of a view/pure function.

        Args:
            transaction_id: The transaction ID
            params: Parameters for the transaction

        Returns:
            The function result

        Raises:
            httpx.HTTPError: If the request fails
        """
        return await self._client._request(
            "POST",
            self._get_read_url(transaction_id),
            data={"params": params.validate_params()},
        )

    async def get(self, transaction_id: str) -> Transaction:
        """Get a transaction by ID.

        Args:
            transaction_id: The transaction ID

        Returns:
            The transaction

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "GET",
            self._get_get_url(transaction_id),
        )
        return Transaction.model_validate(response)

    async def list(
        self,
        business_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PagedResponse[Transaction]:
        """List transactions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of transactions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "GET",
            self._get_list_url(business_id, params),
        )
        return PagedResponse[Transaction].model_validate(response)

    async def create(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> Transaction:
        """Create a new transaction.

        Args:
            business_id: The business ID
            params: Transaction creation parameters

        Returns:
            The created transaction

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_create_url(business_id),
            data=params,
        )
        return Transaction.model_validate(response)

    async def import_from_abi(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> List[Transaction]:
        """Import transactions from an ABI.

        Args:
            business_id: The business ID
            params: ABI import parameters

        Returns:
            The imported transactions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_import_from_abi_url(business_id),
            data=params,
        )
        return [Transaction.model_validate(tx) for tx in response]

    async def update(
        self,
        transaction_id: str,
        params: Dict[str, Any],
    ) -> Transaction:
        """Update a transaction.

        Args:
            transaction_id: The transaction ID
            params: Update parameters

        Returns:
            The updated transaction

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "PUT",
            self._get_update_url(transaction_id),
            data=params,
        )
        return Transaction.model_validate(response)

    async def delete(self, transaction_id: str) -> None:
        """Delete a transaction.

        Args:
            transaction_id: The transaction ID

        Raises:
            httpx.HTTPError: If the request fails
        """
        await self._client._request(
            "DELETE",
            self._get_delete_url(transaction_id),
        )

    async def restore(self, transaction_id: str) -> List[Transaction]:
        """Restore a deleted transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The restored transactions

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client._request(
            "PUT",
            self._get_restore_url(transaction_id),
            data={"rewardIds": [transaction_id]},
        )
        return [Transaction.model_validate(tx) for tx in response] 