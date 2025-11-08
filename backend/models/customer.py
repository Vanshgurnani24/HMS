"""
Customer Model - SQLAlchemy ORM Model
Represents customer information in the database.

UPDATED: Added id_proof_path field for storing uploaded ID proof files.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    id_type = Column(String, nullable=True)  # passport, driver_license, national_id
    id_number = Column(String, nullable=True)
    id_proof_path = Column(String, nullable=True)  # <-- NEW: Path to uploaded ID proof file
    date_of_birth = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer")