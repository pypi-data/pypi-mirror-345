"""Common models for the 1Shot API."""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """A generic paged response model.

    Args:
        T: The type of items in the response
    """

    response: List[T] = Field(..., description="The list of items in the current page")
    page: int = Field(..., description="The current page number")
    page_size: int = Field(..., description="The page size")
    total_results: int = Field(..., description="The total number of results") 