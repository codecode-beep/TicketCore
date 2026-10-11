
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_admin

from app.database import get_db
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.services import venue as venue_service

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post(
    "/",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db)
):
    return venue_service.create_venue(db, venue_data)


@router.get("/", response_model=list[VenueResponse])
def list_venues(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return venue_service.list_venues(db, skip, limit)


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    venue = venue_service.get_venue(db, venue_id)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return venue


@router.patch("/{venue_id}", response_model=VenueResponse,dependencies=[Depends(require_admin)])
def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    db: Session = Depends(get_db)
):
    venue = venue_service.update_venue(db, venue_id, venue_data)

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return venue
