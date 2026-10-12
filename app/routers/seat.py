
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.seat import SeatBulkCreate, SeatResponse
from app.services import seat as seat_service
from app.core.dependencies import require_admin

router = APIRouter(tags=["Seats"])


@router.post(
    "/venues/{venue_id}/seats/bulk",
    response_model=list[SeatResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_seats_bulk(
    venue_id: int,
    seat_data: SeatBulkCreate,
    db: Session = Depends(get_db)
):
    return seat_service.create_seats_bulk(db, venue_id, seat_data)


@router.get(
    "/venues/{venue_id}/seats",
    response_model=list[SeatResponse]
)
def list_seats(
    venue_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return seat_service.list_seats(db, venue_id, skip, limit)


@router.get(
    "/seats/{seat_id}",
    response_model=SeatResponse
)
def get_seat(
    seat_id: int,
    db: Session = Depends(get_db)
):
    return seat_service.get_seat(db, seat_id)
