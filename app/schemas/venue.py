from pydantic import BaseModel, Field, ConfigDict

class VenueCreate(BaseModel):
    name: str
    city: str
    state: str
    capacity: int = Field(gt=0)

class VenueUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    capacity: int | None = Field(default=None, gt=0)

class VenueResponse(BaseModel):
    id: int
    name: str
    city: str
    state: str
    capacity: int

    model_config = ConfigDict(from_attributes=True)