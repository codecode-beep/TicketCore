
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Event, Seat, EventSeat
from app.schemas.event_seat import (
    EventSeatBulkCreate,
    EventSeatPriceUpdate,
)


def create_event_seats_bulk(
    db: Session,
    event_id: int,
    seat_data: EventSeatBulkCreate
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if event.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seats can only be assigned to draft events"
        )

    seat_ids = [seat.seat_id for seat in seat_data.seats]

    if len(seat_ids) != len(set(seat_ids)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate seat IDs in request"
        )

    existing_seats = db.scalars(
        select(Seat).where(Seat.id.in_(seat_ids))
    ).all()

    if len(existing_seats) != len(seat_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more physical seats do not exist"
        )

    for seat in existing_seats:
        if seat.venue_id != event.venue_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="All seats must belong to the event's venue"
            )

    event_seats = [
        EventSeat(
            event_id=event_id,
            seat_id=seat.seat_id,
            price=seat.price
        )
        for seat in seat_data.seats
    ]

    try:
        db.add_all(event_seats)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more seats are already assigned to this event"
        )

    return event_seats


def list_event_seats(
    db: Session,
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    seat_status: str | None = None
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    stmt = select(EventSeat).where(EventSeat.event_id == event_id)

    if seat_status is not None:
        stmt = stmt.where(EventSeat.status == seat_status)

    stmt = (
        stmt.order_by(EventSeat.id)
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(stmt).all()


def get_event_seat(
    db: Session,
    event_id: int,
    event_seat_id: int
):
    event_seat = db.scalar(
        select(EventSeat).where(
            EventSeat.id == event_seat_id,
            EventSeat.event_id == event_id
        )
    )

    if event_seat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event seat not found"
        )

    return event_seat


def update_event_seat_price(
    db: Session,
    event_id: int,
    event_seat_id: int,
    price_data: EventSeatPriceUpdate
):
    event_seat = get_event_seat(db, event_id, event_seat_id)

    if event_seat.status != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot change the price of a held or sold seat"
        )

    if event_seat.event.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prices can only be changed for draft events"
        )

    event_seat.price = price_data.price
    event_seat.version += 1

    db.commit()
    db.refresh(event_seat)

    return event_seat
