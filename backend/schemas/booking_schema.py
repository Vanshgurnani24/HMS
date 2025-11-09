"""
Booking Pydantic schemas for request/response validation.
Handles booking data validation, creation, updates, and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from models.booking import BookingStatus


# Booking Schemas
class BookingBase(BaseModel):
    customer_id: int = Field(..., gt=0, description="Customer ID")
    room_id: int = Field(..., gt=0, description="Room ID")
    check_in_date: date = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out_date: date = Field(..., description="Check-out date (YYYY-MM-DD)")
    number_of_guests: int = Field(..., gt=0, description="Number of guests")
    special_requests: Optional[str] = None
    
    @field_validator('check_out_date')
    @classmethod
    def validate_dates(cls, check_out_date, info):
        """Validate that check-out is after check-in"""
        check_in_date = info.data.get('check_in_date')
        if check_in_date and check_out_date <= check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return check_out_date


class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    discount: Optional[float] = Field(0.0, ge=0, description="Discount amount")
    tax_percentage: Optional[float] = Field(12.0, ge=0, le=100, description="Tax percentage (default: 12%)")


class BookingUpdate(BaseModel):
    """Schema for updating booking details"""
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    number_of_guests: Optional[int] = Field(None, gt=0)
    special_requests: Optional[str] = None
    discount: Optional[float] = Field(None, ge=0)
    
    @field_validator('check_out_date')
    @classmethod
    def validate_dates(cls, check_out_date, info):
        """Validate that check-out is after check-in if both provided"""
        check_in_date = info.data.get('check_in_date')
        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return check_out_date


class BookingStatusUpdate(BaseModel):
    """Schema for updating only booking status"""
    status: BookingStatus


class BookingResponse(BookingBase):
    """Schema for booking response (includes all fields)"""
    id: int
    booking_reference: str
    created_by: int
    number_of_nights: int
    room_price: float
    total_amount: float
    discount: float
    tax: float
    final_amount: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for paginated booking list response"""
    total: int
    bookings: list[BookingResponse]


class BookingDetailResponse(BookingResponse):
    """Schema for detailed booking response with related data"""
    customer_name: str
    customer_email: str
    customer_phone: str
    room_number: str
    room_type: str
    created_by_username: str


class BookingReceipt(BaseModel):
    """Schema for booking receipt"""
    booking_reference: str
    customer_name: str
    customer_email: str
    room_number: str
    room_type: str
    check_in_date: date
    check_out_date: date
    number_of_nights: int
    number_of_guests: int
    room_price_per_night: float
    subtotal: float
    discount: float
    tax: float
    final_amount: float
    booking_status: str
    created_at: datetime
    special_requests: Optional[str] = None


class BookingAvailabilityCheck(BaseModel):
    """Schema for checking room availability"""
    room_id: int
    check_in_date: date
    check_out_date: date
    
    @field_validator('check_out_date')
    @classmethod
    def validate_dates(cls, check_out_date, info):
        check_in_date = info.data.get('check_in_date')
        if check_in_date and check_out_date <= check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return check_out_date


class BookingAvailabilityResponse(BaseModel):
    """Schema for availability check response"""
    available: bool
    message: str
    conflicting_bookings: Optional[list[str]] = None
