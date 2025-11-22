from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class HotelSettings(Base):
    __tablename__ = "hotel_settings"

    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, nullable=False, default="My Hotel")
    hotel_address = Column(String, nullable=True)
    hotel_phone = Column(String, nullable=True)
    hotel_email = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
