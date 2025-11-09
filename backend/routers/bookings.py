"""
Booking Management Router
Handles all booking-related operations including creation, updates, cancellation, and receipt generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime, date
import uuid

from database import get_db
from models.booking import Booking, BookingStatus
from models.room import Room, RoomStatus
from models.customer import Customer
from models.user import User, UserRole
from schemas.booking_schema import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingDetailResponse,
    BookingStatusUpdate,
    BookingReceipt,
    BookingAvailabilityCheck,
    BookingAvailabilityResponse
)
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/bookings", tags=["Booking Management"])


def generate_booking_reference() -> str:
    """Generate unique booking reference"""
    return f"BK{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def calculate_nights(check_in: date, check_out: date) -> int:
    """Calculate number of nights between dates"""
    return (check_out - check_in).days


def calculate_booking_cost(room_price: float, nights: int, discount: float = 0.0, tax_percentage: float = 12.0) -> dict:
    """Calculate booking costs including tax and discount"""
    total_amount = room_price * nights
    discount_amount = discount
    subtotal = total_amount - discount_amount
    tax_amount = (subtotal * tax_percentage) / 100
    final_amount = subtotal + tax_amount
    
    return {
        "room_price": room_price,
        "total_amount": total_amount,
        "discount": discount_amount,
        "tax": tax_amount,
        "final_amount": round(final_amount, 2)
    }


def check_room_availability(db: Session, room_id: int, check_in: date, check_out: date, exclude_booking_id: Optional[int] = None) -> tuple[bool, list]:
    """
    Check if room is available for the given date range.
    Returns (is_available, conflicting_bookings)
    """
    # Query for overlapping bookings
    query = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
        or_(
            # New booking starts during existing booking
            and_(Booking.check_in_date <= check_in, Booking.check_out_date > check_in),
            # New booking ends during existing booking
            and_(Booking.check_in_date < check_out, Booking.check_out_date >= check_out),
            # New booking completely contains existing booking
            and_(Booking.check_in_date >= check_in, Booking.check_out_date <= check_out)
        )
    )
    
    # Exclude current booking if updating
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    conflicting_bookings = query.all()
    
    return len(conflicting_bookings) == 0, conflicting_bookings


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Create a new booking with automatic cost calculation and room availability validation.
    
    **Process:**
    1. Validates customer and room exist
    2. Checks room availability for date range
    3. Calculates number of nights and total cost
    4. Creates booking with PENDING status
    5. Updates room status to RESERVED
    
    **Business Rules:**
    - Check-out date must be after check-in date
    - Room must be available (not booked) for the entire date range
    - Number of guests cannot exceed room capacity
    - Automatic calculation of nights, tax, and final amount
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {booking.customer_id} not found"
        )
    
    # Validate room exists
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {booking.room_id} not found"
        )
    
    # Check if room is active
    if not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room {room.room_number} is not active"
        )
    
    # Check room capacity
    if booking.number_of_guests > room.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of guests ({booking.number_of_guests}) exceeds room capacity ({room.capacity})"
        )
    
    # Check if check-in date is not in the past
    if booking.check_in_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past"
        )
    
    # Check room availability
    is_available, conflicting = check_room_availability(
        db, booking.room_id, booking.check_in_date, booking.check_out_date
    )
    
    if not is_available:
        conflict_details = [
            f"Booking {b.booking_reference} ({b.check_in_date} to {b.check_out_date})"
            for b in conflicting
        ]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": f"Room {room.room_number} is not available for the selected dates",
                "conflicting_bookings": conflict_details
            }
        )
    
    # Calculate nights and costs
    nights = calculate_nights(booking.check_in_date, booking.check_out_date)
    costs = calculate_booking_cost(
        room.price_per_night,
        nights,
        booking.discount,
        booking.tax_percentage
    )
    
    # Generate unique booking reference
    booking_reference = generate_booking_reference()
    
    # Create new booking
    new_booking = Booking(
        booking_reference=booking_reference,
        customer_id=booking.customer_id,
        room_id=booking.room_id,
        created_by=current_user.id,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_guests=booking.number_of_guests,
        number_of_nights=nights,
        room_price=room.price_per_night,
        total_amount=costs["total_amount"],
        discount=costs["discount"],
        tax=costs["tax"],
        final_amount=costs["final_amount"],
        status=BookingStatus.PENDING,
        special_requests=booking.special_requests
    )
    
    # Update room status to RESERVED
    room.status = RoomStatus.RESERVED
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking


@router.get("/", response_model=BookingListResponse)
def get_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    check_in_date: Optional[date] = Query(None, description="Filter by check-in date"),
    booking_reference: Optional[str] = Query(None, description="Search by booking reference"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all bookings with optional filters and pagination.
    
    **Filters:**
    - **status**: Filter by booking status (pending, confirmed, checked_in, checked_out, cancelled)
    - **customer_id**: Filter by customer
    - **room_id**: Filter by room
    - **check_in_date**: Filter by check-in date
    - **booking_reference**: Search by booking reference
    
    **Pagination:**
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return (max 100)
    """
    query = db.query(Booking)
    
    # Apply filters
    if status:
        query = query.filter(Booking.status == status)
    if customer_id:
        query = query.filter(Booking.customer_id == customer_id)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    if check_in_date:
        query = query.filter(Booking.check_in_date == check_in_date)
    if booking_reference:
        query = query.filter(Booking.booking_reference.ilike(f"%{booking_reference}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by creation date (newest first)
    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "bookings": bookings
    }


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific booking including customer and room details.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Build detailed response with related data
    booking_detail = {
        **booking.__dict__,
        "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}",
        "customer_email": booking.customer.email,
        "customer_phone": booking.customer.phone,
        "room_number": booking.room.room_number,
        "room_type": booking.room.room_type.value,
        "created_by_username": booking.created_by_user.username
    }
    
    return booking_detail


@router.get("/reference/{booking_reference}", response_model=BookingDetailResponse)
def get_booking_by_reference(
    booking_reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking details by booking reference number.
    
    Useful for customer inquiries and quick lookups.
    """
    booking = db.query(Booking).filter(Booking.booking_reference == booking_reference).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with reference '{booking_reference}' not found"
        )
    
    booking_detail = {
        **booking.__dict__,
        "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}",
        "customer_email": booking.customer.email,
        "customer_phone": booking.customer.phone,
        "room_number": booking.room.room_number,
        "room_type": booking.room.room_type.value,
        "created_by_username": booking.created_by_user.username
    }
    
    return booking_detail


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update booking details (dates, guests, special requests, discount).
    
    **Note:** 
    - If dates are changed, availability is re-checked
    - Costs are automatically recalculated
    - Cannot update cancelled or checked-out bookings
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Check if booking can be modified
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.CHECKED_OUT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify {booking.status.value} booking"
        )
    
    # Get update data
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Check if dates are being changed
    new_check_in = update_data.get("check_in_date", booking.check_in_date)
    new_check_out = update_data.get("check_out_date", booking.check_out_date)
    
    # If dates changed, check availability
    if new_check_in != booking.check_in_date or new_check_out != booking.check_out_date:
        is_available, conflicting = check_room_availability(
            db, booking.room_id, new_check_in, new_check_out, exclude_booking_id=booking_id
        )
        
        if not is_available:
            conflict_details = [
                f"Booking {b.booking_reference} ({b.check_in_date} to {b.check_out_date})"
                for b in conflicting
            ]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Room is not available for the new dates",
                    "conflicting_bookings": conflict_details
                }
            )
        
        # Recalculate nights and costs
        nights = calculate_nights(new_check_in, new_check_out)
        discount = update_data.get("discount", booking.discount)
        costs = calculate_booking_cost(booking.room_price, nights, discount)
        
        booking.check_in_date = new_check_in
        booking.check_out_date = new_check_out
        booking.number_of_nights = nights
        booking.total_amount = costs["total_amount"]
        booking.discount = costs["discount"]
        booking.tax = costs["tax"]
        booking.final_amount = costs["final_amount"]
    
    # Update other fields
    if "number_of_guests" in update_data:
        # Check room capacity
        if update_data["number_of_guests"] > booking.room.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Number of guests exceeds room capacity ({booking.room.capacity})"
            )
        booking.number_of_guests = update_data["number_of_guests"]
    
    if "special_requests" in update_data:
        booking.special_requests = update_data["special_requests"]
    
    # Recalculate if only discount changed
    if "discount" in update_data and new_check_in == booking.check_in_date:
        costs = calculate_booking_cost(
            booking.room_price,
            booking.number_of_nights,
            update_data["discount"]
        )
        booking.discount = costs["discount"]
        booking.tax = costs["tax"]
        booking.final_amount = costs["final_amount"]
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update booking status (confirm, check-in, check-out).
    
    **Status Flow:**
    - PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
    - Can cancel at any stage before check-out
    
    **Automatic Actions:**
    - CONFIRMED: Room status remains RESERVED
    - CHECKED_IN: Room status → OCCUPIED, timestamp recorded
    - CHECKED_OUT: Room status → AVAILABLE, timestamp recorded
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Validate status transitions
    new_status = status_update.status
    current_status = booking.status
    
    # Cannot change from CANCELLED or CHECKED_OUT
    if current_status in [BookingStatus.CANCELLED, BookingStatus.CHECKED_OUT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {current_status.value}"
        )
    
    # Update status and handle room status changes
    booking.status = new_status
    
    if new_status == BookingStatus.CONFIRMED:
        booking.room.status = RoomStatus.RESERVED
    
    elif new_status == BookingStatus.CHECKED_IN:
        booking.room.status = RoomStatus.OCCUPIED
        booking.checked_in_at = datetime.utcnow()
    
    elif new_status == BookingStatus.CHECKED_OUT:
        booking.room.status = RoomStatus.AVAILABLE
        booking.checked_out_at = datetime.utcnow()
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Cancel a booking and update room status back to AVAILABLE.
    
    **Business Rules:**
    - Cannot cancel already checked-out or cancelled bookings
    - Room status is automatically set to AVAILABLE
    - Cancellation is permanent
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Check if booking can be cancelled
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    if booking.status == BookingStatus.CHECKED_OUT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel checked-out booking"
        )
    
    # Cancel booking and free up the room
    booking.status = BookingStatus.CANCELLED
    booking.room.status = RoomStatus.AVAILABLE
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/{booking_id}/receipt", response_model=BookingReceipt)
def get_booking_receipt(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate booking receipt with complete booking and payment details.
    
    Returns a structured receipt suitable for printing or PDF generation.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    receipt = BookingReceipt(
        booking_reference=booking.booking_reference,
        customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
        customer_email=booking.customer.email,
        room_number=booking.room.room_number,
        room_type=booking.room.room_type.value,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_nights=booking.number_of_nights,
        number_of_guests=booking.number_of_guests,
        room_price_per_night=booking.room_price,
        subtotal=booking.total_amount - booking.discount,
        discount=booking.discount,
        tax=booking.tax,
        final_amount=booking.final_amount,
        booking_status=booking.status.value,
        created_at=booking.created_at,
        special_requests=booking.special_requests
    )
    
    return receipt


@router.post("/check-availability", response_model=BookingAvailabilityResponse)
def check_availability(
    availability_check: BookingAvailabilityCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a room is available for booking in the specified date range.
    
    Returns availability status and conflicting bookings if any.
    """
    # Validate room exists
    room = db.query(Room).filter(Room.id == availability_check.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {availability_check.room_id} not found"
        )
    
    # Check availability
    is_available, conflicting = check_room_availability(
        db,
        availability_check.room_id,
        availability_check.check_in_date,
        availability_check.check_out_date
    )
    
    if is_available:
        return BookingAvailabilityResponse(
            available=True,
            message=f"Room {room.room_number} is available for the selected dates"
        )
    else:
        conflict_details = [
            f"{b.booking_reference} ({b.check_in_date} to {b.check_out_date})"
            for b in conflicting
        ]
        return BookingAvailabilityResponse(
            available=False,
            message=f"Room {room.room_number} is not available",
            conflicting_bookings=conflict_details
        )


@router.get("/customer/{customer_id}/bookings", response_model=BookingListResponse)
def get_customer_bookings(
    customer_id: int,
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings for a specific customer.
    
    Useful for customer history and loyalty programs.
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    query = db.query(Booking).filter(Booking.customer_id == customer_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    
    return {
        "total": len(bookings),
        "bookings": bookings
    }


@router.get("/room/{room_id}/bookings", response_model=BookingListResponse)
def get_room_bookings(
    room_id: int,
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings for a specific room.
    
    Useful for room history and maintenance scheduling.
    """
    # Validate room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    query = db.query(Booking).filter(Booking.room_id == room_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    
    return {
        "total": len(bookings),
        "bookings": bookings
    }


@router.get("/today/checkins", response_model=BookingListResponse)
def get_todays_checkins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings scheduled for check-in today.
    
    Useful for front desk operations.
    """
    today = date.today()
    
    bookings = db.query(Booking).filter(
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
    ).all()
    
    return {
        "total": len(bookings),
        "bookings": bookings
    }


@router.get("/today/checkouts", response_model=BookingListResponse)
def get_todays_checkouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings scheduled for check-out today.
    
    Useful for housekeeping and front desk operations.
    """
    today = date.today()
    
    bookings = db.query(Booking).filter(
        Booking.check_out_date == today,
        Booking.status == BookingStatus.CHECKED_IN
    ).all()
    
    return {
        "total": len(bookings),
        "bookings": bookings
    }