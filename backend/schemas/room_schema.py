from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.room import RoomStatus


# Room Schemas
class RoomBase(BaseModel):
    room_number: str
    room_type: str  # Changed from RoomType enum to str for dynamic room types
    price_per_night: float = Field(..., gt=0, description="Price must be greater than 0")
    floor: int = Field(..., ge=0, description="Floor number")
    capacity: int = Field(..., gt=0, description="Room capacity")
    description: Optional[str] = None
    amenities: Optional[str] = None  # Comma-separated values


class RoomCreate(RoomBase):
    """Schema for creating a new room"""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating room details (all fields optional)"""
    room_number: Optional[str] = None
    room_type: Optional[str] = None  # Changed from RoomType enum to str
    status: Optional[RoomStatus] = None
    price_per_night: Optional[float] = Field(None, gt=0)
    floor: Optional[int] = Field(None, ge=0)
    capacity: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    amenities: Optional[str] = None
    is_active: Optional[bool] = None


class RoomStatusUpdate(BaseModel):
    """Schema for updating only room status"""
    status: RoomStatus


class RoomResponse(RoomBase):
    """Schema for room response (includes all fields)"""
    id: int
    status: RoomStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    """Schema for paginated room list response"""
    total: int
    rooms: list[RoomResponse]