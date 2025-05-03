from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class OrCondition:
    field: str
    operator: str  # eq, neq, gt, gte, lt, lte, like, ilike etc.
    value: Any


class BasePageParams(BaseModel):
    page: int = Field(default=1, ge=1, description="page number")
    page_size: int = Field(default=10, ge=1, le=1000, description="page size")


class PageParams(BaseModel, Generic[T]):
    page: int = Field(default=1, ge=1, description="page number")
    page_size: int = Field(default=10, ge=1, le=1000, description="page size")
    order_by: Optional[str] = Field(default=None, description="order by field")
    order_direction: Optional[str] = Field(default="asc", description="asc or desc")
    eq_conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="list of equality conditions, each as a dict with key and value",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @model_validator(mode="after")
    def validate_eq_conditions(self) -> "PageParams[T]":
        if self.eq_conditions:
            args = self.__class__.__pydantic_generic_metadata__["args"]
            if not args:
                return self

            model_type = args[0]
            if isinstance(model_type, TypeVar):
                return self

            model_fields = model_type.model_fields.keys()
            invalid_keys = set(self.eq_conditions.keys()) - set(model_fields)
            if invalid_keys:
                raise ValueError(f"Invalid keys in eq_conditions: {invalid_keys}")
        return self


class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusStatisticsPageResponse(PageResponse, Generic[T]):
    """
    please append the statistical field: pending,failed .....
    """

    success: int = 0
    failed: int = 0
    cancelled: int = 0
