
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from .. import database, models, oauth2
from ..schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationCancelResponse
)
from ..services import reservation as reservation_service


router = APIRouter(tags=["Reservations"])


# Create reservation
@router.post(
    "/events/{event_id}/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reservation(
    event_id: int,
    reservation_data: ReservationCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return reservation_service.create_reservation(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        reservation_data=reservation_data
    )


# List reservations of logged-in user
@router.get(
    "/reservations",
    response_model=list[ReservationResponse]
)
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return reservation_service.list_reservations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


# Get reservation by ID
@router.get(
    "/reservations/{reservation_id}",
    response_model=ReservationResponse
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return reservation_service.get_reservation(
        db=db,
        reservation_id=reservation_id,
        user_id=current_user.id
    )


# Cancel reservation
@router.delete(
    "/reservations/{reservation_id}",
    response_model=ReservationCancelResponse
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return reservation_service.cancel_reservation(
        db=db,
        reservation_id=reservation_id,
        user_id=current_user.id
    )
