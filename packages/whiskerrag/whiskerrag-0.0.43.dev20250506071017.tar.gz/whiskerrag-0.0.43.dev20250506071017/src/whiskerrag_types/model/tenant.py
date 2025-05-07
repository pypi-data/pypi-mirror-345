import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from whiskerrag_types.model.utils import parse_datetime


class Tenant(BaseModel):
    tenant_id: str = Field(
        default_factory=lambda: str(uuid4()), description="tenant id"
    )
    tenant_name: str = Field("", description="tenant name")
    email: str = Field(..., description="email")
    secret_key: str = Field("", description="secret_key")
    is_active: bool = Field(True, description="is active")
    metadata: Optional[dict] = Field(
        None, description="Metadata for the tenant", alias="metadata"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="tenant created time",
        alias="gmt_create",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="tenant updated time",
        alias="gmt_modified",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def update(self, **kwargs: Any) -> "Tenant":
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.updated_at = datetime.now()
        return self

    @field_validator("is_active", mode="before")
    @classmethod
    def convert_tinyint_to_bool(cls, v: Any) -> bool:
        return bool(v)

    @model_validator(mode="before")
    def pre_process_data(cls, data: dict) -> dict:
        for field, value in data.items():
            if isinstance(value, UUID):
                data[field] = str(value)
            if field == "metadata" and isinstance(value, str):
                data[field] = json.loads(value)
        field_mappings = {"created_at": "gmt_create", "updated_at": "gmt_modified"}
        for field, alias_name in field_mappings.items():
            val = data.get(field) or data.get(alias_name)
            if val is None:
                continue

            if isinstance(val, str):
                dt = parse_datetime(val)
                data[field] = dt
                data[alias_name] = dt
            else:
                if val and val.tzinfo is None:
                    dt = val.replace(tzinfo=timezone.utc)
                    data[field] = dt
                    data[alias_name] = dt

        return data

    @model_validator(mode="after")
    def set_defaults(self) -> "Tenant":
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        return self

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
