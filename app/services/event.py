
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, Venue
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventStatusUpdate,
)


def create_event(db: Session, venue_id: int, event_data: EventCreate):
    venue = db.get(Venue, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    if event_data.starts_at.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Event start time must include a timezone"
        )

    event = Event(
        venue_id=venue_id,
        **event_data.model_dump()
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_event(db: Session, event_id: int):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


def list_events(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    event_status: str | None = None,
    venue_id: int | None = None
):
    stmt = select(Event)

    if event_status is not None:
        stmt = stmt.where(Event.status == event_status)

    if venue_id is not None:
        stmt = stmt.where(Event.venue_id == venue_id)

    stmt = (
        stmt.order_by(Event.starts_at, Event.id)
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(stmt).all()


def update_event(
    db: Session,
    event_id: int,
    event_data: EventUpdate
):
    event = get_event(db, event_id)

    update_data = event_data.model_dump(exclude_unset=True)

    if "starts_at" in update_data:
        starts_at = update_data["starts_at"]

        if starts_at is None or starts_at.utcoffset() is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Event start time must include a timezone"
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


ALLOWED_TRANSITIONS = {
    "draft": {"active", "cancelled"},
    "active": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def update_event_status(
    db: Session,
    event_id: int,
    status_data: EventStatusUpdate
):
    event = get_event(db, event_id)

    new_status = status_data.status

    if new_status not in ALLOWED_TRANSITIONS[event.status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change event status from {event.status} to {new_status}"
        )

    event.status = new_status

    db.commit()
    db.refresh(event)

    return event
