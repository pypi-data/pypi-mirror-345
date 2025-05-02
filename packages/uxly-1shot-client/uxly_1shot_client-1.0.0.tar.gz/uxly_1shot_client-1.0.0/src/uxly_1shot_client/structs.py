"""Structs module for the 1Shot API."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from uxly_1shot_client.models.struct import SolidityStruct, SolidityStructParam


class StructUpdateParams(BaseModel):
    """Parameters for updating a struct."""

    name: str = Field(..., description="The new name for the struct")


class NewSolidityStructParam(BaseModel):
    """Parameters for creating a new struct parameter."""

    name: str = Field(..., description="The parameter name")
    description: Optional[str] = Field(None, description="The parameter description")
    type: str = Field(..., description="The parameter type")
    index: int = Field(..., description="The parameter index")
    value: Optional[str] = Field(None, description="The parameter value")
    type_size: Optional[int] = Field(None, description="The parameter type size")
    type_size2: Optional[int] = Field(None, description="The parameter type size 2")
    is_array: bool = Field(..., description="Whether the parameter is an array")
    array_size: Optional[int] = Field(None, description="The array size")
    type_struct_id: Optional[str] = Field(None, description="The type struct ID")
    type_struct: Optional[Dict[str, Any]] = Field(None, description="The type struct")


class StructParamUpdateRequest(BaseModel):
    """Parameters for updating a struct parameter."""

    id: str = Field(..., description="The parameter ID")
    name: Optional[str] = Field(None, description="The parameter name")
    description: Optional[str] = Field(None, description="The parameter description")
    type: Optional[str] = Field(None, description="The parameter type")
    index: Optional[int] = Field(None, description="The parameter index")
    value: Optional[str] = Field(None, description="The parameter value")
    type_size: Optional[int] = Field(None, description="The parameter type size")
    type_size2: Optional[int] = Field(None, description="The parameter type size 2")
    is_array: Optional[bool] = Field(None, description="Whether the parameter is an array")
    array_size: Optional[int] = Field(None, description="The array size")
    type_struct_id: Optional[str] = Field(None, description="The type struct ID")
    type_struct: Optional[Dict[str, Any]] = Field(None, description="The type struct")


class Structs:
    """Structs module for the 1Shot API."""

    def __init__(self, client: Union["SyncClient", "AsyncClient"]) -> None:
        """Initialize the structs module.

        Args:
            client: The client instance
        """
        self._client = client

    def _get_update_url(self, struct_id: str) -> str:
        """Get the URL for updating a struct.

        Args:
            struct_id: The struct ID

        Returns:
            The URL for updating a struct
        """
        return f"/structs/{struct_id}"

    def _get_add_param_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for adding a parameter to a struct.

        Args:
            business_id: The business ID
            struct_id: The struct ID

        Returns:
            The URL for adding a parameter to a struct
        """
        return f"/business/{business_id}/structs/{struct_id}/params"

    def _get_update_params_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for updating parameters of a struct.

        Args:
            business_id: The business ID
            struct_id: The struct ID

        Returns:
            The URL for updating parameters of a struct
        """
        return f"/business/{business_id}/structs/{struct_id}/params"

    def _get_remove_param_url(self, struct_id: str, struct_param_id: str) -> str:
        """Get the URL for removing a parameter from a struct.

        Args:
            struct_id: The struct ID
            struct_param_id: The parameter ID

        Returns:
            The URL for removing a parameter from a struct
        """
        return f"/structs/{struct_id}/params/{struct_param_id}"


class SyncStructs(Structs):
    """Synchronous structs module for the 1Shot API."""

    def update(self, struct_id: str, params: StructUpdateParams) -> SolidityStruct:
        """Update an existing solidity struct.

        Args:
            struct_id: The ID of the struct to update
            params: Update parameters

        Returns:
            The updated struct

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "PUT",
            self._get_update_url(struct_id),
            data=params.model_dump(),
        )
        return SolidityStruct.model_validate(response)

    def add_param(
        self, business_id: str, struct_id: str, param: NewSolidityStructParam
    ) -> SolidityStruct:
        """Add a parameter to an existing struct.

        Args:
            business_id: The business ID that owns the struct
            struct_id: The ID of the struct to add the parameter to
            param: The new parameter to add

        Returns:
            The updated struct

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "POST",
            self._get_add_param_url(business_id, struct_id),
            data=param.model_dump(exclude_none=True),
        )
        return SolidityStruct.model_validate(response)

    def update_params(
        self,
        business_id: str,
        struct_id: str,
        updates: List[StructParamUpdateRequest],
    ) -> SolidityStruct:
        """Update multiple parameters of a struct.

        Args:
            business_id: The business ID that owns the struct
            struct_id: The ID of the struct to update
            updates: Array of parameter updates

        Returns:
            The updated struct

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "PUT",
            self._get_update_params_url(business_id, struct_id),
            data={"updates": [update.model_dump(exclude_none=True) for update in updates]},
        )
        return SolidityStruct.model_validate(response)

    def remove_param(self, struct_id: str, struct_param_id: str) -> SolidityStruct:
        """Remove a parameter from a struct.

        Args:
            struct_id: The ID of the struct
            struct_param_id: The ID of the parameter to remove

        Returns:
            The updated struct

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client.request(
            "DELETE",
            self._get_remove_param_url(struct_id, struct_param_id),
        )
        return SolidityStruct.model_validate(response)


class AsyncStructs(Structs):
    """Asynchronous structs module for the 1Shot API."""

    async def update(self, struct_id: str, params: StructUpdateParams) -> SolidityStruct:
        """Update an existing solidity struct.

        Args:
            struct_id: The ID of the struct to update
            params: Update parameters

        Returns:
            The updated struct

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "PUT",
            self._get_update_url(struct_id),
            data=params.model_dump(),
        )
        return SolidityStruct.model_validate(response)

    async def add_param(
        self, business_id: str, struct_id: str, param: NewSolidityStructParam
    ) -> SolidityStruct:
        """Add a parameter to an existing struct.

        Args:
            business_id: The business ID that owns the struct
            struct_id: The ID of the struct to add the parameter to
            param: The new parameter to add

        Returns:
            The updated struct

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "POST",
            self._get_add_param_url(business_id, struct_id),
            data=param.model_dump(exclude_none=True),
        )
        return SolidityStruct.model_validate(response)

    async def update_params(
        self,
        business_id: str,
        struct_id: str,
        updates: List[StructParamUpdateRequest],
    ) -> SolidityStruct:
        """Update multiple parameters of a struct.

        Args:
            business_id: The business ID that owns the struct
            struct_id: The ID of the struct to update
            updates: Array of parameter updates

        Returns:
            The updated struct

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "PUT",
            self._get_update_params_url(business_id, struct_id),
            data={"updates": [update.model_dump(exclude_none=True) for update in updates]},
        )
        return SolidityStruct.model_validate(response)

    async def remove_param(self, struct_id: str, struct_param_id: str) -> SolidityStruct:
        """Remove a parameter from a struct.

        Args:
            struct_id: The ID of the struct
            struct_param_id: The ID of the parameter to remove

        Returns:
            The updated struct

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self._client.request(
            "DELETE",
            self._get_remove_param_url(struct_id, struct_param_id),
        )
        return SolidityStruct.model_validate(response) 