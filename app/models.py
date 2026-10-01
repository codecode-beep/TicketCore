from .database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP,text, ForeignKey,UniqueConstraint, func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String)
    role = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())
    

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True,nullable=False)
    city = Column(String,nullable=False)
    state = Column(String,nullable=False)
    capacity = Column(Integer,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class Seat(Base):
    __tablename__ = "seats"

    __table_args__ = (
    UniqueConstraint(
        "venue_id",
        "section",
        "row",
        "seat_number",
        name="uq_physical_seat"
    ),
    )

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False) 
    section = Column(String,nullable=False)
    row = Column(String,nullable=False)
    seat_number = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False) 
    name = Column(String, index=True,nullable=False)
    description = Column(String)
    starts_at = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String,nullable=False, default="draft")
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class EventSeat(Base):
    __tablename__ = "event_seats"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "seat_id",
            name="uq_event_seat"
        ),
    )
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False) 
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False) 
    price = Column(Integer,nullable=False)
    status = Column(String,nullable=False, default="available")
    version = Column(Integer,nullable=False, default=1)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) 
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False) 
    status = Column(String,nullable=False, default="pending")
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class ReservationSeat(Base):
    __tablename__ = "reservation_seats"

    __table_args__ = (
    UniqueConstraint(
        "reservation_id",
        "event_seat_id",
        name="uq_reservation_event_seat"
    ),
    )

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False) 
    event_seat_id = Column(Integer, ForeignKey("event_seats.id", ondelete="CASCADE"), nullable=False) 
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False) 
    amount = Column(Integer,nullable=False)
    currency = Column(String,nullable=False)
    status = Column(String, nullable=False,default="pending")
    provider = Column(String,nullable=False)
    provider_reference = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, unique=True) 
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Integer,nullable=False) 
    status = Column(String,nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now(),onupdate=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False) 
    event_seat_id = Column(Integer, ForeignKey("event_seats.id", ondelete="CASCADE"), nullable=False,unique=True) 
    price = Column(Integer,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=func.now())
    
