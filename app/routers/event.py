
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventStatusUpdate,
    EventResponse,
    EventStatus,
)
from app.services import event as event_service

from app.core.dependencies import require_admin
router = APIRouter(tags=["Events"])


@router.post(
    "/venues/{venue_id}/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_event(
    venue_id: int,
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    return event_service.create_event(db, venue_id, event_data)


@router.get("/events", response_model=list[EventResponse])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_status: EventStatus | None = None,
    venue_id: int | None = None,
    db: Session = Depends(get_db)
):
    return event_service.list_events(
        db=db,
        skip=skip,
        limit=limit,
        event_status=event_status,
        venue_id=venue_id
    )


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    return event_service.get_event(db, event_id)


@router.patch(
    "/events/{event_id}",
    response_model=EventResponse,
    dependencies=[Depends(require_admin)]
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):
    return event_service.update_event(db, event_id, event_data)


@router.patch(
    "/events/{event_id}/status",
    response_model=EventResponse,
    dependencies=[Depends(require_admin)]
)
def update_event_status(
    event_id: int,
    status_data: EventStatusUpdate,
    db: Session = Depends(get_db)
):
    return event_service.update_event_status(db, event_id, status_data)
