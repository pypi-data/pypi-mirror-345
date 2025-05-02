"""Struct operations for the 1Shot API."""

from typing import Any, Dict, List, Optional, Union

from .models.struct import (
    SolidityStruct,
    SolidityStructParam,
    NewSolidityStructParam,
    StructUpdateParams,
    StructParamUpdateRequest,
)
from .models.common import PagedResponse
from .base import BaseClient


class Structs(BaseClient):
    """Struct operations for the 1Shot API."""

    def _get_update_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for updating a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}"

    def _get_add_param_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for adding a parameter to a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/param"

    def _get_update_params_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for updating parameters in a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/params"

    def _get_remove_param_url(self, business_id: str, struct_id: str, param_id: str) -> str:
        """Get the URL for removing a parameter from a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/param/{param_id}"

    def list(self, business_id: str) -> List[SolidityStruct]:
        """List all structs for a business.

        Args:
            business_id: The business ID.

        Returns:
            A list of structs.
        """
        url = f"{self.base_url}/business/{business_id}/structs"
        response = self._request("GET", url)
        return [SolidityStruct(**struct) for struct in response]

    def get(self, business_id: str, struct_id: str) -> SolidityStruct:
        """Get a struct by ID.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.

        Returns:
            The struct.
        """
        url = f"{self.base_url}/business/{business_id}/struct/{struct_id}"
        response = self._request("GET", url)
        return SolidityStruct(**response)

    def update(self, business_id: str, struct_id: str, params: StructUpdateParams) -> SolidityStruct:
        """Update a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            params: The update parameters.

        Returns:
            The updated struct.
        """
        url = self._get_update_url(business_id, struct_id)
        response = self._request("PUT", url, json=params.dict(by_alias=True))
        return SolidityStruct(**response)

    def add_param(self, business_id: str, struct_id: str, param: NewSolidityStructParam) -> SolidityStructParam:
        """Add a parameter to a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            param: The parameter to add.

        Returns:
            The added parameter.
        """
        url = self._get_add_param_url(business_id, struct_id)
        response = self._request("POST", url, json=param.dict(by_alias=True))
        return SolidityStructParam(**response)

    def update_params(self, business_id: str, struct_id: str, params: List[StructParamUpdateRequest]) -> List[SolidityStructParam]:
        """Update parameters in a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            params: The parameters to update.

        Returns:
            The updated parameters.
        """
        url = self._get_update_params_url(business_id, struct_id)
        response = self._request("PUT", url, json=[param.dict(by_alias=True) for param in params])
        return [SolidityStructParam(**param) for param in response]

    def remove_param(self, business_id: str, struct_id: str, param_id: str) -> None:
        """Remove a parameter from a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            param_id: The parameter ID.
        """
        url = self._get_remove_param_url(business_id, struct_id, param_id)
        self._request("DELETE", url)


class AsyncStructs(BaseClient):
    """Async struct operations for the 1Shot API."""

    def _get_update_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for updating a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}"

    def _get_add_param_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for adding a parameter to a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/param"

    def _get_update_params_url(self, business_id: str, struct_id: str) -> str:
        """Get the URL for updating parameters in a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/params"

    def _get_remove_param_url(self, business_id: str, struct_id: str, param_id: str) -> str:
        """Get the URL for removing a parameter from a struct."""
        return f"{self.base_url}/business/{business_id}/struct/{struct_id}/param/{param_id}"

    async def list(self, business_id: str) -> List[SolidityStruct]:
        """List all structs for a business.

        Args:
            business_id: The business ID.

        Returns:
            A list of structs.
        """
        url = f"{self.base_url}/business/{business_id}/structs"
        response = await self._request("GET", url)
        return [SolidityStruct(**struct) for struct in response]

    async def get(self, business_id: str, struct_id: str) -> SolidityStruct:
        """Get a struct by ID.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.

        Returns:
            The struct.
        """
        url = f"{self.base_url}/business/{business_id}/struct/{struct_id}"
        response = await self._request("GET", url)
        return SolidityStruct(**response)

    async def update(self, business_id: str, struct_id: str, params: StructUpdateParams) -> SolidityStruct:
        """Update a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            params: The update parameters.

        Returns:
            The updated struct.
        """
        url = self._get_update_url(business_id, struct_id)
        response = await self._request("PUT", url, json=params.dict(by_alias=True))
        return SolidityStruct(**response)

    async def add_param(self, business_id: str, struct_id: str, param: NewSolidityStructParam) -> SolidityStructParam:
        """Add a parameter to a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            param: The parameter to add.

        Returns:
            The added parameter.
        """
        url = self._get_add_param_url(business_id, struct_id)
        response = await self._request("POST", url, json=param.dict(by_alias=True))
        return SolidityStructParam(**response)

    async def update_params(self, business_id: str, struct_id: str, params: List[StructParamUpdateRequest]) -> List[SolidityStructParam]:
        """Update parameters in a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            params: The parameters to update.

        Returns:
            The updated parameters.
        """
        url = self._get_update_params_url(business_id, struct_id)
        response = await self._request("PUT", url, json=[param.dict(by_alias=True) for param in params])
        return [SolidityStructParam(**param) for param in response]

    async def remove_param(self, business_id: str, struct_id: str, param_id: str) -> None:
        """Remove a parameter from a struct.

        Args:
            business_id: The business ID.
            struct_id: The struct ID.
            param_id: The parameter ID.
        """
        url = self._get_remove_param_url(business_id, struct_id, param_id)
        await self._request("DELETE", url) 