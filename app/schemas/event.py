
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EventStatus = Literal["draft", "active", "cancelled", "completed"]


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    starts_at: datetime


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    starts_at: datetime | None = None


class EventStatusUpdate(BaseModel):
    status: EventStatus


class EventResponse(BaseModel):
    id: int
    venue_id: int
    name: str
    description: str | None
    starts_at: datetime
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
