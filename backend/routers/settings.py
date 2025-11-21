"""
Hotel Settings Router
Handles hotel configuration like name, contact details, etc.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models.settings import HotelSettings

router = APIRouter(prefix="/settings", tags=["settings"])


# Pydantic schemas
class HotelSettingsBase(BaseModel):
    hotel_name: str
    hotel_address: Optional[str] = None
    hotel_phone: Optional[str] = None
    hotel_email: Optional[str] = None


class HotelSettingsResponse(HotelSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HotelSettingsUpdate(BaseModel):
    hotel_name: Optional[str] = None
    hotel_address: Optional[str] = None
    hotel_phone: Optional[str] = None
    hotel_email: Optional[str] = None


@router.get("/hotel", response_model=HotelSettingsResponse)
def get_hotel_settings(db: Session = Depends(get_db)):
    """Get hotel settings. Creates default settings if none exist."""
    settings = db.query(HotelSettings).first()

    if not settings:
        # Create default settings
        settings = HotelSettings(
            hotel_name="My Hotel",
            hotel_address="",
            hotel_phone="",
            hotel_email=""
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/hotel", response_model=HotelSettingsResponse)
def update_hotel_settings(
    settings_update: HotelSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update hotel settings."""
    settings = db.query(HotelSettings).first()

    if not settings:
        # Create new settings if none exist
        settings = HotelSettings(
            hotel_name=settings_update.hotel_name or "My Hotel",
            hotel_address=settings_update.hotel_address or "",
            hotel_phone=settings_update.hotel_phone or "",
            hotel_email=settings_update.hotel_email or ""
        )
        db.add(settings)
    else:
        # Update existing settings
        if settings_update.hotel_name is not None:
            settings.hotel_name = settings_update.hotel_name
        if settings_update.hotel_address is not None:
            settings.hotel_address = settings_update.hotel_address
        if settings_update.hotel_phone is not None:
            settings.hotel_phone = settings_update.hotel_phone
        if settings_update.hotel_email is not None:
            settings.hotel_email = settings_update.hotel_email

    db.commit()
    db.refresh(settings)
    return settings
