"""Transaction models for the 1Shot API."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ListTransactionsParams(BaseModel):
    """Parameters for listing transactions.
    
    Args:
        page_size: The size of the page to return. Defaults to 25
        page: Which page to return. This is 1 indexed, and defaults to the first page, 1
        chain_id: The specific chain to get transactions for
        name: Filter transactions by name
        status: Filter by deletion status - 'live', 'archived', or 'both'
        contract_address: Filter by contract address
    """
    
    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and defaults to the first page, 1")
    chain_id: Optional[int] = Field(None, alias="chainId", description="The specific chain to get transactions for")
    name: Optional[str] = Field(None, description="Filter transactions by name")
    status: Optional[str] = Field(None, description="Filter by deletion status")
    contract_address: Optional[str] = Field(None, alias="contractAddress", description="Filter by contract address")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['live', 'archived', 'both']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of {valid_statuses}')
        return v

    @validator('page')
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page must be greater than or equal to 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page size must be greater than or equal to 1')
        return v


class Transaction(BaseModel):
    """A transaction model."""

    id: str = Field(..., description="internal ID of the transaction object")
    business_id: str = Field(..., alias="businessId", description="The business that owns this transaction")
    chain: int = Field(..., description="The chain ID")
    contract_address: str = Field(..., alias="contractAddress", description="The contract address")
    escrow_wallet_id: str = Field(..., alias="escrowWalletId", description="Name of the escrowWallet that owns the transaction")
    name: str = Field(..., description="Name of transaction")
    description: str = Field(..., description="Description of transaction")
    function_name: str = Field(..., alias="functionName", description="Name of the function on the contract to call for this transaction")
    state_mutability: str = Field(..., alias="stateMutability", description="The state mutability")
    inputs: List[Dict[str, Any]] = Field(..., description="The input parameters")
    outputs: List[Dict[str, Any]] = Field(..., description="The output parameters")
    callback_url: Optional[str] = Field(None, alias="callbackUrl", description="The current destination for webhooks to be sent when this transaction is executed. Will be null if no webhook is assigned.")
    public_key: Optional[str] = Field(None, alias="publicKey", description="The current public key for verifying the integrity of the webhook when this transaction is executed. 1Shot will sign its webhooks with a private key and provide a signature for the webhook that can be validated with this key. It will be null if there is no webhook destination specified.")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the transaction is deleted")


class TransactionExecution(BaseModel):
    """Transaction execution model."""

    id: str = Field(..., description="internal ID of the transaction execution")
    transaction_id: str = Field(..., alias="transactionId", description="internal ID of the transaction")
    api_credential_id: Optional[str] = Field(None, alias="apiCredentialId", description="ID of the API Credential used to execute the transaction. Note, this is not the API Key itself. This will be null if a user initiated the execution and not an API Credential")
    api_key: Optional[str] = Field(None, alias="apiKey", description="The actual API key used")
    user_id: Optional[str] = Field(None, alias="userId", description="The User ID that executed the transaction. This will be null if an API key was used instead of a user token.")
    status: str = Field(..., description="The execution status")
    chain_transaction_id: Optional[str] = Field(None, alias="chainTransactionId", description="The ID of the actual chain transaction in the internal chain service.")
    transaction_hash: Optional[str] = Field(None, alias="transactionHash", description="The hash of the transaction. Only calculated once the status is Submitted.")
    name: str = Field(..., description="the name of the associated Transaction. Included as a convienience.")
    function_name: str = Field(..., alias="functionName", description="The functionName of the associated Transaction. Included as a convienience.")
    chain: int = Field(..., description="The chain ID")
    memo: Optional[str] = Field(None, description="Optional text supplied when the transaction is executed. This can be a note to the user about why the execution was done, or formatted information such as JSON that can be used by the user's system.")
    completed: Optional[int] = Field(None, description="The completion timestamp")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the execution is deleted")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Pending','Submitted', 'Completed', 'Retrying', 'Failed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class TransactionEstimate(BaseModel):
    """Transaction cost estimate model."""

    chain: int = Field(..., description="The chain ID")
    contract_address: str = Field(..., alias="contractAddress", description="The contract address")
    function_name: str = Field(..., alias="functionName", description="The function name")
    gas_amount: str = Field(..., alias="gasAmount", description="The amount of gas units it will use")
    max_fee_per_gas: Optional[str] = Field(None, alias="maxFeePerGas", description="The maximum fee per gas")
    max_priority_fee_per_gas: Optional[str] = Field(None, alias="maxPriorityFeePerGas", description="The maximum priority fee per gas")
    gas_price: Optional[str] = Field(None, alias="gasPrice", description="The gas price")


class TransactionTestResult(BaseModel):
    """Transaction test result model."""

    success: bool = Field(..., description="Whether the test was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="The test result")
    error: Optional[str] = Field(None, description="The error message if any")
    gas_used: Optional[int] = Field(None, alias="gasUsed", description="The gas used in the test")
    logs: Optional[List[Dict[str, Any]]] = Field(None, description="The transaction logs")


class TransactionCreateParams(BaseModel):
    """Parameters for creating a transaction.
    
    Args:
        chain: The chain ID
        contract_address: The contract address
        name: Name of the transaction
        description: Description of the transaction
        function_name: Name of the function on the contract to call
        state_mutability: The state mutability
        inputs: The input parameters
        outputs: The output parameters
        callback_url: Optional URL for webhook callbacks
    """
    
    chain: int = Field(..., description="The chain ID")
    contract_address: str = Field(..., alias="contractAddress", description="The contract address")
    name: str = Field(..., description="Name of the transaction")
    description: str = Field(..., description="Description of the transaction")
    function_name: str = Field(..., alias="functionName", description="Name of the function on the contract to call")
    state_mutability: str = Field(..., alias="stateMutability", description="The state mutability")
    inputs: List[Dict[str, Any]] = Field(..., description="The input parameters")
    outputs: List[Dict[str, Any]] = Field(..., description="The output parameters")
    callback_url: Optional[str] = Field(None, alias="callbackUrl", description="Optional URL for webhook callbacks")

    @validator('state_mutability')
    def validate_state_mutability(cls, v):
        valid_mutabilities = ['pure', 'view', 'nonpayable', 'payable']
        if v not in valid_mutabilities:
            raise ValueError(f'State mutability must be one of {valid_mutabilities}')
        return v


class TransactionUpdateParams(BaseModel):
    """Parameters for updating a transaction.
    
    Args:
        name: Optional new name for the transaction
        description: Optional new description for the transaction
        callback_url: Optional new callback URL for webhooks
    """
    
    name: Optional[str] = Field(None, description="New name for the transaction")
    description: Optional[str] = Field(None, description="New description for the transaction")
    callback_url: Optional[str] = Field(None, alias="callbackUrl", description="New callback URL for webhooks") 