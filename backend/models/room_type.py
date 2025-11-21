from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class RoomTypeConfig(Base):
    """
    Dynamic room type configuration.
    Just stores the type name/label. Room-specific details (price, capacity, description)
    are set on individual rooms.
    """
    __tablename__ = "room_type_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Internal name: "single", "double", "suite"
    display_name = Column(String, nullable=False)  # Display name: "Single Room", "Deluxe Suite"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
