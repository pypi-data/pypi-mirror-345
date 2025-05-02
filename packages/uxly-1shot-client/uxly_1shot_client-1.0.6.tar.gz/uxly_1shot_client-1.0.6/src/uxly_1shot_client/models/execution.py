"""Models for transaction executions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionExecution(BaseModel):
    """A single execution of a transaction- ie, a function call"""

    id: str = Field(..., description="internal ID of the transaction execution")
    transaction_id: str = Field(..., alias="transactionId", description="internal ID of the transaction")
    api_credential_id: Optional[str] = Field(
        None, 
        alias="apiCredentialId", 
        description="ID of the API Credential used to execute the transaction. Note, this is not the API Key itself. This will be null if a user initiated the execution and not an API Credential"
    )
    api_key: Optional[str] = Field(
        None,
        alias="apiKey",
        description="The actual API key used"
    )
    user_id: Optional[str] = Field(
        None, 
        alias="userId", 
        description="The User ID that executed the transaction. This will be null if an API key was used instead of a user token."
    )
    status: str = Field(
        ...,
        description="Current status of the execution",
        pattern="^(Submitted|Completed|Retrying|Failed)$",
    )
    chain_transaction_id: Optional[str] = Field(
        None, 
        alias="chainTransactionId", 
        description="The ID of the actual chain transaction in the internal chain service."
    )
    transaction_hash: Optional[str] = Field(
        None, 
        alias="transactionHash", 
        description="The hash of the transaction. Only calculated once the status is Submitted."
    )
    name: str = Field(
        ...,
        description="the name of the associated Transaction. Included as a convienience."
    )
    function_name: str = Field(
        ...,
        alias="functionName",
        description="The functionName of the associated Transaction. Included as a convienience."
    )
    chain: int = Field(
        ...,
        description="The chain ID"
    )
    memo: Optional[str] = Field(
        None, 
        description="Optional text supplied when the transaction is executed. This can be a note to the user about why the execution was done, or formatted information such as JSON that can be used by the user's system."
    )
    completed: Optional[int] = Field(
        None,
        description="The completion timestamp"
    )
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the execution is deleted")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True
        alias_generator = lambda x: x.replace("_", "")
