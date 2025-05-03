import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from whiskerrag_types.model.utils import parse_datetime


class TaskRestartRequest(BaseModel):
    task_id_list: List[str] = Field(..., description="List of task IDs to restart")


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELED = "canceled"
    PENDING_RETRY = "pending_retry"


class Task(BaseModel):
    task_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the task",
        alias="task_id",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current status of the task",
        alias="status",
    )
    knowledge_id: str = Field(
        ..., description="Identifier for the source file", alias="knowledge_id"
    )
    metadata: Optional[dict] = Field(
        None, description="Metadata for the task", alias="metadata"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message (only present if the task failed)",
        alias="error_message",
    )
    space_id: str = Field(..., description="Identifier for the space", alias="space_id")
    user_id: Optional[str] = Field(
        None, description="Identifier for the user", alias="user_id"
    )
    tenant_id: str = Field(
        ..., description="Identifier for the tenant", alias="tenant_id"
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="Task creation time",
        alias="gmt_create",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update time",
        alias="gmt_modified",
    )

    def update(self, **kwargs: Any) -> "Task":
        if "created_at" in kwargs:
            raise ValueError("created_at is a read-only field and cannot be modified")
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.updated_at = datetime.now(timezone.utc)
        return self

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
    def set_defaults(self) -> "Task":
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
