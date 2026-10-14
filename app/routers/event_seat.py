
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event_seat import (
    EventSeatBulkCreate,
    EventSeatPriceUpdate,
    EventSeatResponse,
)
from app.services import event_seat as event_seat_service

from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/events/{event_id}/seats",
    tags=["Event Seats"]
)


@router.post(
    "/bulk",
    response_model=list[EventSeatResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_event_seats_bulk(
    event_id: int,
    seat_data: EventSeatBulkCreate,
    db: Session = Depends(get_db)
):
    return event_seat_service.create_event_seats_bulk(
        db, event_id, seat_data
    )


@router.get(
    "/",
    response_model=list[EventSeatResponse]
)
def list_event_seats(
    event_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    seat_status: str | None = None,
    db: Session = Depends(get_db)
):
    return event_seat_service.list_event_seats(
        db, event_id, skip, limit, seat_status
    )


@router.get(
    "/{event_seat_id}",
    response_model=EventSeatResponse
)
def get_event_seat(
    event_id: int,
    event_seat_id: int,
    db: Session = Depends(get_db)
):
    return event_seat_service.get_event_seat(
        db, event_id, event_seat_id
    )


@router.patch(
    "/{event_seat_id}/price",
    response_model=EventSeatResponse,
    dependencies=[Depends(require_admin)]
)
def update_event_seat_price(
    event_id: int,
    event_seat_id: int,
    price_data: EventSeatPriceUpdate,
    db: Session = Depends(get_db)
):
    return event_seat_service.update_event_seat_price(
        db, event_id, event_seat_id, price_data
    )
