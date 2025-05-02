"""Transaction models for the 1Shot API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class Transaction(BaseModel):
    """A transaction model."""

    id: str = Field(..., description="The transaction ID")
    business_id: str = Field(..., description="The business ID")
    chain: int = Field(..., description="The chain ID")
    contract_address: str = Field(..., description="The contract address")
    escrow_wallet_id: str = Field(..., description="The escrow wallet ID")
    name: str = Field(..., description="The transaction name")
    description: str = Field(..., description="The transaction description")
    function_name: str = Field(..., description="The function name")
    state_mutability: str = Field(..., description="The state mutability")
    inputs: List[Dict[str, Any]] = Field(..., description="The input parameters")
    outputs: List[Dict[str, Any]] = Field(..., description="The output parameters")
    callback_url: Optional[str] = Field(None, description="The callback URL")
    public_key: Optional[str] = Field(None, description="The public key")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the transaction is deleted")


class TransactionExecution(BaseModel):
    """Transaction execution model."""

    id: str = Field(..., description="The execution ID")
    transaction_id: str = Field(..., description="The transaction ID")
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


class TransactionParams(BaseModel):
    """Base model for transaction parameters."""

    def validate_params(self) -> Dict[str, Any]:
        """Validate and return the parameters as a dictionary."""
        return self.model_dump(exclude_none=True)


class TransactionEstimate(BaseModel):
    """Transaction cost estimate model."""

    gas_limit: int = Field(..., description="The estimated gas limit")
    gas_price: str = Field(..., description="The estimated gas price")
    total_cost: str = Field(..., description="The total estimated cost")
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
    gas_used: Optional[int] = Field(None, description="The gas used in the test")
    logs: Optional[List[Dict[str, Any]]] = Field(None, description="The transaction logs") 