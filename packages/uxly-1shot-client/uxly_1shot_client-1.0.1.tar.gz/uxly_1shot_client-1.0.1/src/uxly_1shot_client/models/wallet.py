"""Wallet models for the 1Shot API."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AccountBalanceDetails(BaseModel):
    """Account balance details model."""

    type: str = Field(..., description="The balance type")
    ticker: str = Field(..., description="The token ticker")
    chain_id: int = Field(..., description="The chain ID")
    token_address: str = Field(..., description="The token address")
    account_address: str = Field(..., description="The account address")
    balance: str = Field(..., description="The balance as a Big Number String")
    decimals: int = Field(..., description="The number of decimals")
    usd_value: float = Field(..., description="The current USD value")
    usd_value_timestamp: int = Field(..., description="The USD value timestamp")


class EscrowWallet(BaseModel):
    """Escrow wallet model."""

    id: str = Field(..., description="The wallet ID")
    account_address: str = Field(..., description="The account address")
    business_id: Optional[str] = Field(None, description="The business ID")
    user_id: Optional[str] = Field(None, description="The user ID")
    chain_id: int = Field(..., description="The chain ID")
    name: str = Field(..., description="The wallet name")
    description: Optional[str] = Field(None, description="The wallet description")
    is_admin: bool = Field(..., description="Whether the wallet is an admin wallet")
    account_balance_details: Optional[AccountBalanceDetails] = Field(
        None, description="The account balance details"
    )
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp") 