
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, EventSeat, Reservation, ReservationSeat
from app.schemas.reservation import ReservationCreate


def create_reservation(
    db: Session,
    event_id: int,
    user_id: int,
    reservation_data: ReservationCreate
):
    seat_ids = reservation_data.event_seat_ids

    if len(seat_ids) != len(set(seat_ids)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate seat IDs in request"
        )

    try:
        event = db.get(Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if event.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event is not active"
            )

        now = datetime.now(timezone.utc)

        if event.starts_at <= now:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event has already started"
            )

        stmt = (
            select(EventSeat)
            .where(
                EventSeat.id.in_(seat_ids),
                EventSeat.event_id == event_id
            )
            .order_by(EventSeat.id)
            .with_for_update()     #PostgreSQl row locking to prevent race conditions(double booking for single seat)
        )

        event_seats = db.scalars(stmt).all()

        if len(event_seats) != len(seat_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more seats do not belong to this event"
            )

        for event_seat in event_seats:
            if event_seat.status != "available":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Seat {event_seat.id} is not available"
                )

        reservation = Reservation(
            user_id=user_id,
            event_id=event_id,
            status="pending",
            expires_at=now + timedelta(minutes=5)    #Set reservation expiration time to 5 minutes from now
        )

        db.add(reservation)
        db.flush()

        for event_seat in event_seats:
            db.add(
                ReservationSeat(
                    reservation_id=reservation.id,
                    event_seat_id=event_seat.id
                )
            )

            event_seat.status = "held"
            event_seat.version += 1

        db.commit()
        db.refresh(reservation)

        return reservation

    except Exception:
        db.rollback()
        raise


def get_reservation(
    db: Session,
    reservation_id: int,
    user_id: int
):
    reservation = db.scalar(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user_id
        )
    )

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    return reservation

def list_reservations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
):
    stmt = (
        select(Reservation)
        .where(Reservation.user_id == user_id)
        .order_by(Reservation.created_at.desc(), Reservation.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(stmt).all()

def lock_reservation_seats(
    db: Session,
    reservation_id: int
):
    stmt = (
        select(EventSeat)
        .join(
            ReservationSeat,
            ReservationSeat.event_seat_id == EventSeat.id
        )
        .where(ReservationSeat.reservation_id == reservation_id)
        .order_by(EventSeat.id)
        .with_for_update(of=EventSeat)
    )

    return db.scalars(stmt).all()


def cancel_reservation(
    db: Session,
    reservation_id: int,
    user_id: int
):
    try:
        reservation = get_reservation(db, reservation_id, user_id)

        event_seats = lock_reservation_seats(db, reservation_id)

        db.refresh(reservation)

        if reservation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only pending reservations can be cancelled"
            )

        reservation.status = "cancelled"

        for event_seat in event_seats:
            if event_seat.status == "held":
                event_seat.status = "available"
                event_seat.version += 1

        db.commit()
        db.refresh(reservation)

        return reservation

    except Exception:
        db.rollback()
        raise

def expire_reservation(
    db: Session,
    reservation_id: int
):
    try:
        reservation = db.get(Reservation, reservation_id)

        if reservation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )

        event_seats = lock_reservation_seats(db, reservation_id)

        db.refresh(reservation)

        if reservation.status != "pending":
            db.rollback()
            return reservation

        now = datetime.now(timezone.utc)

        if reservation.expires_at > now:
            db.rollback()
            return reservation

        reservation.status = "expired"

        for event_seat in event_seats:
            if event_seat.status == "held":
                event_seat.status = "available"
                event_seat.version += 1

        db.commit()
        db.refresh(reservation)

        return reservation

    except Exception:
        db.rollback()
        raise


def expire_old_reservations(
    db: Session,
    limit: int = 100
):
    now = datetime.now(timezone.utc)

    stmt = (
        select(Reservation.id)
        .where(
            Reservation.status == "pending",
            Reservation.expires_at <= now
        )
        .order_by(Reservation.expires_at, Reservation.id)
        .limit(limit)
    )

    reservation_ids = db.scalars(stmt).all()

    expired_count = 0

    for reservation_id in reservation_ids:
        reservation = expire_reservation(db, reservation_id)

        if reservation.status == "expired":
            expired_count += 1

    return expired_count