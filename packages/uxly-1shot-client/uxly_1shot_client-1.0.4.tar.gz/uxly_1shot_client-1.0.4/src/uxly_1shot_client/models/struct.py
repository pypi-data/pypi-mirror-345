"""Struct models for the 1Shot API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SolidityStructParam(BaseModel):
    """A parameter in a Solidity struct."""

    id: str = Field(..., description="The parameter ID")
    struct_id: str = Field(..., alias="structId", description="The struct ID")
    name: str = Field(..., description="The parameter name")
    description: Optional[str] = Field(None, description="The parameter description")
    type: str = Field(..., description="The parameter type")
    index: int = Field(..., description="The parameter index")
    value: Optional[str] = Field(None, description="The parameter value")
    type_size: Optional[int] = Field(None, alias="typeSize", description="The parameter type size")
    type_size2: Optional[int] = Field(None, alias="typeSize2", description="The parameter type size 2")
    is_array: bool = Field(..., alias="isArray", description="Whether the parameter is an array")
    array_size: Optional[int] = Field(None, alias="arraySize", description="The array size")
    type_struct_id: Optional[str] = Field(None, alias="typeStructId", description="The type struct ID")
    type_struct: Optional["SolidityStruct"] = Field(None, alias="typeStruct", description="The type struct")


class SolidityStruct(BaseModel):
    """A Solidity struct."""

    id: str = Field(..., description="The struct ID")
    business_id: str = Field(..., alias="businessId", description="The business ID")
    name: str = Field(..., description="The struct name")
    params: List[SolidityStructParam] = Field(..., description="The struct parameters")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")
    deleted: bool = Field(..., description="Whether the struct is deleted")


# Update the forward reference
SolidityStructParam.model_rebuild() 