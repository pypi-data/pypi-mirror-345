"""Models for transaction executions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionExecution(BaseModel):
    """A single execution of a transaction."""

    id: str = Field(..., description="Internal ID of the transaction execution")
    transaction_id: str = Field(..., alias="transactionId", description="Internal ID of the transaction")
    api_credential_id: Optional[str] = Field(
        None, alias="apiCredentialId", description="ID of the API Credential used to execute the transaction"
    )
    user_id: Optional[str] = Field(
        None, alias="userId", description="The User ID that executed the transaction"
    )
    status: str = Field(
        ...,
        description="Current status of the execution",
        pattern="^(Submitted|Completed|Retrying|Failed)$",
    )
    chain_transaction_id: Optional[str] = Field(
        None, alias="chainTransactionId", description="The ID of the actual chain transaction"
    )
    transaction_hash: Optional[str] = Field(
        None, alias="transactionHash", description="The hash of the transaction on the chain"
    )
    memo: Optional[str] = Field(
        None, description="Optional text supplied when the transaction is executed"
    )
    completed_timestamp: Optional[datetime] = Field(
        None, alias="completedTimestamp", description="Timestamp when the execution was completed"
    )
    updated: datetime = Field(..., description="Timestamp of last update")
    created: datetime = Field(..., description="Timestamp of creation")
    deleted: bool = Field(..., description="Whether the execution has been deleted")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True
        alias_generator = lambda x: x.replace("_", "")
