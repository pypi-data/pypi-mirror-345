"""Transaction models for the 1Shot API."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class Transaction(BaseModel):
    """A transaction model."""

    id: str = Field(..., description="The transaction ID")
    business_id: str = Field(..., alias="businessId", description="The business ID")
    chain: int = Field(..., description="The chain ID")
    contract_address: str = Field(..., alias="contractAddress", description="The contract address")
    escrow_wallet_id: str = Field(..., alias="escrowWalletId", description="The escrow wallet ID")
    name: str = Field(..., description="The transaction name")
    description: str = Field(..., description="The transaction description")
    function_name: str = Field(..., alias="functionName", description="The function name")
    state_mutability: str = Field(..., alias="stateMutability", description="The state mutability")
    params: List[Dict[str, Any]] = Field(..., description="The input parameters")
    outputs: Optional[List[Dict[str, Any]]] = Field(None, description="The output parameters")
    callback_url: Optional[str] = Field(None, alias="callbackUrl", description="The callback URL")
    public_key: Optional[str] = Field(None, alias="publicKey", description="The public key")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the transaction is deleted")


class TransactionExecution(BaseModel):
    """Transaction execution model."""

    id: str = Field(..., description="The execution ID")
    transaction_id: str = Field(..., alias="transactionId", description="The transaction ID")
    status: str = Field(..., description="The execution status")
    params: Dict[str, Any] = Field(..., description="The execution parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="The execution result")
    error: Optional[str] = Field(None, description="The error message if any")
    created: int = Field(..., description="The creation timestamp")
    updated: int = Field(..., description="The last update timestamp")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class TransactionEstimate(BaseModel):
    """Transaction cost estimate model."""

    gas_limit: int = Field(..., alias="gasLimit", description="The estimated gas limit")
    gas_price: str = Field(..., alias="gasPrice", description="The estimated gas price")
    total_cost: str = Field(..., alias="totalCost", description="The total estimated cost")
    currency: str = Field(..., description="The currency of the cost estimate")

    @validator('gas_limit')
    def validate_gas_limit(cls, v):
        if v <= 0:
            raise ValueError('Gas limit must be positive')
        return v

    @validator('gas_price')
    def validate_gas_price(cls, v):
        try:
            float(v)
        except ValueError:
            raise ValueError('Gas price must be a valid number')
        return v


class TransactionTestResult(BaseModel):
    """Transaction test result model."""

    success: bool = Field(..., description="Whether the test was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="The test result")
    error: Optional[str] = Field(None, description="The error message if any")
    gas_used: Optional[int] = Field(None, alias="gasUsed", description="The gas used in the test")
    logs: Optional[List[Dict[str, Any]]] = Field(None, description="The transaction logs") 