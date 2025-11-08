from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String, unique=True, index=True, nullable=False)
    
    # Foreign Keys
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Booking Details
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    number_of_nights = Column(Integer, nullable=False)
    
    # Pricing
    room_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    special_requests = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    checked_in_at = Column(DateTime, nullable=True)
    checked_out_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    created_by_user = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")