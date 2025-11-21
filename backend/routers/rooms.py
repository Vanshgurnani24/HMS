from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.room import Room, RoomStatus
from models.user import User, UserRole
from schemas.room_schema import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomListResponse,
    RoomStatusUpdate
)
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/rooms", tags=["Room Management"])


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def add_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Create a new room (Admin only).
    
    - **room_number**: Unique room identifier (e.g., "101", "A-205")
    - **room_type**: single, double, suite, or deluxe
    - **price_per_night**: Room price per night
    - **floor**: Floor number
    - **capacity**: Maximum occupancy
    - **description**: Room description (optional)
    - **amenities**: Comma-separated amenities (e.g., "WiFi, AC, TV")
    """
    # Check if room number already exists
    existing_room = db.query(Room).filter(Room.room_number == room.room_number).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room number '{room.room_number}' already exists"
        )
    
    # Create new room
    new_room = Room(
        room_number=room.room_number,
        room_type=room.room_type,
        price_per_night=room.price_per_night,
        floor=room.floor,
        capacity=room.capacity,
        description=room.description,
        amenities=room.amenities,
        status=RoomStatus.AVAILABLE  # New rooms are available by default
    )
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    return new_room


@router.get("/", response_model=RoomListResponse)
def get_rooms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    status: Optional[RoomStatus] = Query(None, description="Filter by status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    floor: Optional[int] = Query(None, ge=0, description="Filter by floor"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all rooms with optional filters.
    
    **Filters:**
    - **room_type**: Filter by room type
    - **status**: Filter by availability status
    - **min_price/max_price**: Filter by price range
    - **floor**: Filter by floor number
    - **is_active**: Show only active/inactive rooms
    
    **Pagination:**
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return (max 100)
    """
    query = db.query(Room)
    
    # Apply filters
    if room_type:
        query = query.filter(Room.room_type == room_type)
    if status:
        query = query.filter(Room.status == status)
    if min_price is not None:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Room.price_per_night <= max_price)
    if floor is not None:
        query = query.filter(Room.floor == floor)
    if is_active is not None:
        query = query.filter(Room.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    rooms = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "rooms": rooms
    }


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific room by ID.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def edit_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Update room details (Admin only).
    
    You can update any combination of fields:
    - room_number, room_type, status, price_per_night
    - floor, capacity, description, amenities, is_active
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Check if new room number already exists (if updating room_number)
    if room_update.room_number and room_update.room_number != room.room_number:
        existing_room = db.query(Room).filter(
            Room.room_number == room_update.room_number,
            Room.id != room_id
        ).first()
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room number '{room_update.room_number}' already exists"
            )
    
    # Update fields
    update_data = room_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    
    return room


@router.patch("/{room_id}/status", response_model=RoomResponse)
def update_room_status(
    room_id: int,
    status_update: RoomStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update room status (Admin and Staff can update).
    
    Available statuses:
    - **available**: Room is ready for booking
    - **occupied**: Room is currently occupied
    - **maintenance**: Room is under maintenance
    - **reserved**: Room is reserved
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    room.status = status_update.status
    db.commit()
    db.refresh(room)
    
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete a room (Admin only).
    
    **Warning**: This permanently deletes the room from the database.
    Consider using is_active=False to soft-delete instead.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Check if room has any bookings
    if room.bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete room with existing bookings. Consider deactivating instead."
        )
    
    db.delete(room)
    db.commit()
    
    return None


@router.get("/available/check", response_model=RoomListResponse)
def get_available_rooms(
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    floor: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all available rooms with optional filters.
    
    This endpoint only returns rooms with status='available' and is_active=True.
    """
    query = db.query(Room).filter(
        Room.status == RoomStatus.AVAILABLE,
        Room.is_active == True
    )
    
    # Apply filters
    if room_type:
        query = query.filter(Room.room_type == room_type)
    if min_price is not None:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Room.price_per_night <= max_price)
    if floor is not None:
        query = query.filter(Room.floor == floor)
    
    rooms = query.all()
    
    return {
        "total": len(rooms),
        "rooms": rooms
    }


@router.get("/type/{room_type}", response_model=RoomListResponse)
def get_rooms_by_type(
    room_type: str,
    status: Optional[RoomStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all rooms of a specific type.

    Accepts any room type name configured in the system.
    """
    query = db.query(Room).filter(Room.room_type == room_type)
    
    if status:
        query = query.filter(Room.status == status)
    
    rooms = query.all()
    
    return {
        "total": len(rooms),
        "rooms": rooms
    }