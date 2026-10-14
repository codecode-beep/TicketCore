
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservationCreate(BaseModel):
    event_seat_ids: list[int] = Field(
        min_length=1,
        max_length=10
    )


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservationCancelResponse(BaseModel):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
