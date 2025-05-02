"""Structs module for the 1Shot API."""

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.struct import SolidityStruct


class StructListParams(BaseModel):
    """Parameters for listing structs."""

    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")

    @validator('page')
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page number must be greater than or equal to 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page size must be greater than or equal to 1')
        return v


class StructCreateParams(BaseModel):
    """Parameters for creating a struct."""

    name: str = Field(..., description="The name of the struct")
    description: Optional[str] = Field(None, description="A description of the struct")
    params: list[Dict[str, Any]] = Field(..., description="The parameters of the struct")


class StructUpdateParams(BaseModel):
    """Parameters for updating a struct."""

    name: Optional[str] = Field(None, description="The name of the struct")
    description: Optional[str] = Field(None, description="A description of the struct")
    params: Optional[list[Dict[str, Any]]] = Field(None, description="The parameters of the struct")


class Structs:
    """Structs module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the structs module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_list_url(self, business_id: str) -> str:
        """Get the URL for listing structs.

        Args:
            business_id: The business ID

        Returns:
            The URL for listing structs
        """
        return f"/business/{business_id}/structs"

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a struct.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a struct
        """
        return f"/business/{business_id}/structs"

    def _get_get_url(self, struct_id: str) -> str:
        """Get the URL for getting a struct.

        Args:
            struct_id: The struct ID

        Returns:
            The URL for getting a struct
        """
        return f"/structs/{struct_id}"

    def _get_update_url(self, struct_id: str) -> str:
        """Get the URL for updating a struct.

        Args:
            struct_id: The struct ID

        Returns:
            The URL for updating a struct
        """
        return f"/structs/{struct_id}"

    def _get_delete_url(self, struct_id: str) -> str:
        """Get the URL for deleting a struct.

        Args:
            struct_id: The struct ID

        Returns:
            The URL for deleting a struct
        """
        return f"/structs/{struct_id}"


class SyncStructs(Structs):
    """Synchronous structs module for the 1Shot API."""

    def list(
        self, business_id: str, params: Optional[StructListParams] = None
    ) -> PagedResponse[SolidityStruct]:
        """List structs for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of structs
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = self._client._request("GET", url, params=query_params)
        else:
            response = self._client._request("GET", url)
        return PagedResponse[SolidityStruct].model_validate(response)

    def create(self, business_id: str, params: StructCreateParams) -> SolidityStruct:
        """Create a new struct for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the struct

        Returns:
            The created struct
        """
        url = self._get_create_url(business_id)
        response = self._client._request("POST", url, json=params.dict(exclude_none=True))
        return SolidityStruct.model_validate(response)

    def get(self, struct_id: str) -> SolidityStruct:
        """Get a struct by ID.

        Args:
            struct_id: The struct ID

        Returns:
            The struct
        """
        url = self._get_get_url(struct_id)
        response = self._client._request("GET", url)
        return SolidityStruct.model_validate(response)

    def update(
        self, struct_id: str, params: StructUpdateParams
    ) -> SolidityStruct:
        """Update a struct.

        Args:
            struct_id: The struct ID
            params: Update parameters

        Returns:
            The updated struct
        """
        url = self._get_update_url(struct_id)
        response = self._client._request("PUT", url, json=params.dict(exclude_none=True))
        return SolidityStruct.model_validate(response)

    def delete(self, struct_id: str) -> Dict[str, bool]:
        """Delete a struct.

        Args:
            struct_id: The struct ID

        Returns:
            A dictionary with a success flag
        """
        url = self._get_delete_url(struct_id)
        return self._client._request("DELETE", url)


class AsyncStructs(Structs):
    """Asynchronous structs module for the 1Shot API."""

    async def list(
        self, business_id: str, params: Optional[StructListParams] = None
    ) -> PagedResponse[SolidityStruct]:
        """List structs for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            A paged response of structs
        """
        url = self._get_list_url(business_id)
        if params:
            query_params = params.dict(by_alias=True, exclude_none=True)
            response = await self._client._request("GET", url, params=query_params)
        else:
            response = await self._client._request("GET", url)
        return PagedResponse[SolidityStruct].model_validate(response)

    async def create(self, business_id: str, params: StructCreateParams) -> SolidityStruct:
        """Create a new struct for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the struct

        Returns:
            The created struct
        """
        url = self._get_create_url(business_id)
        response = await self._client._request("POST", url, json=params.dict(exclude_none=True))
        return SolidityStruct.model_validate(response)

    async def get(self, struct_id: str) -> SolidityStruct:
        """Get a struct by ID.

        Args:
            struct_id: The struct ID

        Returns:
            The struct
        """
        url = self._get_get_url(struct_id)
        response = await self._client._request("GET", url)
        return SolidityStruct.model_validate(response)

    async def update(
        self, struct_id: str, params: StructUpdateParams
    ) -> SolidityStruct:
        """Update a struct.

        Args:
            struct_id: The struct ID
            params: Update parameters

        Returns:
            The updated struct
        """
        url = self._get_update_url(struct_id)
        response = await self._client._request("PUT", url, json=params.dict(exclude_none=True))
        return SolidityStruct.model_validate(response)

    async def delete(self, struct_id: str) -> Dict[str, bool]:
        """Delete a struct.

        Args:
            struct_id: The struct ID

        Returns:
            A dictionary with a success flag
        """
        url = self._get_delete_url(struct_id)
        return await self._client._request("DELETE", url) 