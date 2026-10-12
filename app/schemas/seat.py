
from pydantic import BaseModel, ConfigDict, Field


class SeatCreate(BaseModel):
    section: str = Field(min_length=1, max_length=50)
    row: str = Field(min_length=1, max_length=20)
    seat_number: str = Field(min_length=1, max_length=20)


class SeatBulkCreate(BaseModel):
    seats: list[SeatCreate] = Field(min_length=1, max_length=500)


class SeatResponse(BaseModel):
    id: int
    venue_id: int
    section: str
    row: str
    seat_number: str

    model_config = ConfigDict(from_attributes=True)
