
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class Log(BaseModel):
    _type: str
    address: str
    blockHash: str
    blockNumber: int
    data: str
    index: int
    topics: List[str]
    transactionHash: str
    transactionIndex: int

class TransactionReceipt(BaseModel):
    _type: str
    blobGasPrice: Optional[str] = None
    blobGasUsed: Optional[str] = None
    blockHash: str
    blockNumber: int
    contractAddress: Optional[str] = None
    cumulativeGasUsed: str
    from_: str = Field(..., alias="from")
    gasPrice: str
    gasUsed: str
    hash: str
    index: int
    logs: List[Log]
    logsBloom: str
    status: int
    to: str

class FragmentInput(BaseModel):
    arrayChildren: Optional[None]  # Matches null in JSON
    arrayLength: Optional[None]
    baseType: str
    components: Optional[None]
    indexed: bool
    name: str
    type: str

class Fragment(BaseModel):
    anonymous: bool
    inputs: List[FragmentInput]
    name: str
    type: str

class ParsedLogEntry(BaseModel):
    args: List[Union[str, None]]  # Some values might be null
    fragment: Fragment
    name: str
    signature: str
    topic: str

class Data(BaseModel):
    businessId: str
    chain: int
    logs: Optional[List[ParsedLogEntry]] = None
    transaction_execution_id: str = Field(..., alias="transactionExecutionId")
    transaction_execution_memo: Optional[str] = Field(None, alias="transactionExecutionMemo")
    transaction_id: str = Field(..., alias="transactionId")
    transaction_receipt: Optional[TransactionReceipt] = Field(None, alias="transactionReceipt")
    userId: Optional[str] = None

class WebhookPayload(BaseModel):
    eventName: str
    data: Data
    timestamp: int
    apiVersion: int
    signature: str