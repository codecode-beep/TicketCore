from sqlalchemy.orm import Session
from app.models import Venue
from app.schemas.venue import VenueCreate, VenueUpdate
from fastapi import HTTPException, status

#create venue
def create_venue(db: Session, venue_data:VenueCreate):
    venue = Venue(**venue_data.model_dump())
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue

#get venue by id
def get_venue(db: Session, venue_id:int):
    venue=db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return venue

#update venue
def update_venue(db: Session, venue_id:int, venue_data:VenueUpdate):
    venue = get_venue(db, venue_id)
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    update_data = venue_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    db.commit()
    db.refresh(venue)
    return venue

#list venues
def list_venues(db: Session, skip:int=0, limit:int=20):
    return (
        db.query(Venue)
        .order_by(Venue.id)
        .offset(skip)
        .limit(limit)
        .all()
    )