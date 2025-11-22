"""
Room Type Configuration Router
Handles CRUD operations for dynamic room types.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models.room_type import RoomTypeConfig
from models.room import Room

router = APIRouter(prefix="/room-types", tags=["Room Types"])


# Pydantic schemas (simplified - just name and display_name)
class RoomTypeCreate(BaseModel):
    name: Optional[str] = None  # Auto-generated from display_name if not provided
    display_name: str


class RoomTypeUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None


class RoomTypeResponse(BaseModel):
    id: int
    name: str
    display_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomTypeListResponse(BaseModel):
    total: int
    room_types: List[RoomTypeResponse]


def seed_default_room_types(db: Session):
    """Seed default room types if none exist."""
    existing = db.query(RoomTypeConfig).first()
    if existing:
        return  # Already seeded

    default_types = [
        RoomTypeConfig(name="single", display_name="Single Room"),
        RoomTypeConfig(name="double", display_name="Double Room"),
        RoomTypeConfig(name="suite", display_name="Suite"),
        RoomTypeConfig(name="deluxe", display_name="Deluxe Room"),
    ]

    for room_type in default_types:
        db.add(room_type)
    db.commit()


@router.post("/seed-defaults")
def seed_defaults(db: Session = Depends(get_db)):
    """
    Manually seed default room types.
    Use this endpoint for initial setup or to restore default room types.
    """
    seed_default_room_types(db)
    return {"message": "Default room types seeded successfully"}


@router.get("/", response_model=RoomTypeListResponse)
def get_room_types(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all room types."""
    query = db.query(RoomTypeConfig)

    if not include_inactive:
        query = query.filter(RoomTypeConfig.is_active == True)

    room_types = query.order_by(RoomTypeConfig.display_name).all()

    return {
        "total": len(room_types),
        "room_types": room_types
    }


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific room type by ID."""
    room_type = db.query(RoomTypeConfig).filter(RoomTypeConfig.id == room_type_id).first()

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with ID {room_type_id} not found"
        )

    return room_type


@router.post("/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
def create_room_type(
    room_type: RoomTypeCreate,
    db: Session = Depends(get_db)
):
    """Create a new room type."""
    # Generate name from display_name if not provided
    name = room_type.name if room_type.name else room_type.display_name.lower().replace(" ", "_")

    # Check if name already exists
    existing = db.query(RoomTypeConfig).filter(RoomTypeConfig.name == name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room type '{name}' already exists"
        )

    new_room_type = RoomTypeConfig(
        name=name,
        display_name=room_type.display_name
    )

    db.add(new_room_type)
    db.commit()
    db.refresh(new_room_type)

    return new_room_type


@router.put("/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(
    room_type_id: int,
    room_type_update: RoomTypeUpdate,
    db: Session = Depends(get_db)
):
    """Update a room type."""
    room_type = db.query(RoomTypeConfig).filter(RoomTypeConfig.id == room_type_id).first()

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with ID {room_type_id} not found"
        )

    # Update fields
    if room_type_update.display_name is not None:
        room_type.display_name = room_type_update.display_name
    if room_type_update.is_active is not None:
        room_type.is_active = room_type_update.is_active

    db.commit()
    db.refresh(room_type)

    return room_type


@router.delete("/{room_type_id}")
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db)
):
    """Delete a room type (only if no rooms are using it)."""
    room_type = db.query(RoomTypeConfig).filter(RoomTypeConfig.id == room_type_id).first()

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with ID {room_type_id} not found"
        )

    # Check if any rooms are using this type
    rooms_using = db.query(Room).filter(Room.room_type == room_type.name).count()

    if rooms_using > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete room type '{room_type.display_name}'. {rooms_using} room(s) are using this type. Please reassign them first or deactivate this type instead."
        )

    db.delete(room_type)
    db.commit()

    return {"message": f"Room type '{room_type.display_name}' deleted successfully"}
