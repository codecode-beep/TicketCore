
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Seat, Venue
from app.schemas.seat import SeatBulkCreate


def create_seats_bulk(
    db: Session,
    venue_id: int,
    seat_data: SeatBulkCreate
):
    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    seats = [
        Seat(venue_id=venue_id, **seat.model_dump())
        for seat in seat_data.seats
    ]

    try:
        db.add_all(seats)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more seats already exist in this venue"
        )

    return seats


def list_seats(
    db: Session,
    venue_id: int,
    skip: int = 0,
    limit: int = 10
):
    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return (
        db.query(Seat)
        .filter(Seat.venue_id == venue_id)
        .order_by(Seat.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_seat(db: Session, seat_id: int):
    seat = db.get(Seat, seat_id)

    if seat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    return seat
