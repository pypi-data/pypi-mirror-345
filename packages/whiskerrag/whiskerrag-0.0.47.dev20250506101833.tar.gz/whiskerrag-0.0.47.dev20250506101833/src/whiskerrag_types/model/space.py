from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from whiskerrag_types.model.utils import parse_datetime


class SpaceCreate(BaseModel):
    """
    SpaceCreate model for creating space resources.
    Attributes:
        space_name (str): Space name, example: petercat bot group.
        description (str): descrition of the space resource.
        metadata (Dict[str, Any]): metadata of the space resource.such as embedding model name
            and other parameters.
    """

    space_name: str = Field(
        ..., max_length=64, description="name of the space resource"
    )
    description: str = Field(..., max_length=255, description="descrition of the space")
    metadata: Dict[str, Any] = Field(
        default={},
        description="metadata of the space resource",
    )


class Space(SpaceCreate):
    """
    Space model class that extends SpaceCreate.
    Attributes:
        space_id (str): Space ID.
        tenant_id (str): Tenant ID.
        created_at (Optional[datetime]): Creation time, defaults to current time in ISO format.
        updated_at (Optional[datetime]): Update time, defaults to current time in ISO format.
    Methods:
        serialize_created_at(created_at: Optional[datetime]) -> Optional[str]:
            Serializes the created_at attribute to ISO format.
        serialize_updated_at(updated_at: Optional[datetime]) -> Optional[str]:
            Serializes the updated_at attribute to ISO format.
        update(**kwargs) -> 'Space':
            Updates the attributes of the instance with the provided keyword arguments and sets updated_at to the current time.
    """

    space_id: str = Field(default_factory=lambda: str(uuid4()), description="space id")
    created_at: Optional[datetime] = Field(
        default=None,
        alias="gmt_create",
        description="creation time",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        alias="gmt_modified",
        description="update time",
    )

    tenant_id: str = Field(..., description="tenant id")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def update(self, **kwargs: Dict[str, Any]) -> "Space":
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now()
        return self

    @model_validator(mode="before")
    def pre_process_data(cls, data: dict) -> dict:
        for field, value in data.items():
            if isinstance(value, UUID):
                data[field] = str(value)
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
    def set_defaults(self) -> "Space":
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        return self

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class SpaceResponse(Space):
    """
    SpaceResponse model class that extends Space.
    Attributes:
         (str): Space ID.
        total_size Optional[int]: size of the all kowledge in this space.
        knowledge_size Optional[int]: count of the knowledge in this space.
    """

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    storage_size: Optional[int] = Field(
        default=0, description="size of the all kowledge in this space"
    )
    knowledge_count: Optional[int] = Field(
        default=0, description="count of the knowledge in this space"
    )

    def update(self, **kwargs: Dict[str, Any]) -> "SpaceResponse":
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self
