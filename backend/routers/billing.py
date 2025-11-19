"""
Billing and Payment Management Router
Handles payment processing, invoice generation, and billing operations.

FIXED VERSION - Added eager loading with joinedload for booking, customer, and room relationships
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from datetime import datetime
import uuid

from database import get_db
from models.payment import Payment, PaymentMethod, PaymentStatus
from models.booking import Booking, BookingStatus
from models.customer import Customer
from models.room import Room
from models.user import User, UserRole
from schemas.payment_schema import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    InvoiceResponse,
    InvoiceItemDetail,
    PaymentSummary,
    RefundRequest,
    RefundResponse
)
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/payments", tags=["Billing & Payment Management"])


def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


def generate_invoice_number() -> str:
    """Generate invoice number in format INV-yyyyMMddHHmmss"""
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def validate_booking_for_payment(db: Session, booking_id: int) -> Booking:
    """Validate booking exists and is eligible for payment"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot process payment for cancelled booking"
        )
    
    return booking


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Create a new payment record for a booking.
    
    **Process:**
    1. Validates booking exists and is not cancelled
    2. Generates unique transaction ID and invoice number
    3. Creates payment record with PENDING status
    4. Payment can be marked as COMPLETED later
    
    **Payment Methods:**
    - cash
    - credit_card
    - debit_card
    - upi
    - net_banking
    - wallet
    
    **Business Rules:**
    - Cannot create payment for cancelled bookings
    - Payment amount should match booking final amount
    - Automatic transaction ID and invoice number generation
    """
    # Validate booking
    booking = validate_booking_for_payment(db, payment.booking_id)
    
    # Validate payment amount matches booking amount
    if abs(payment.amount - booking.final_amount) > 0.01:  # Allow for floating point precision
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount (${payment.amount:.2f}) does not match booking amount (${booking.final_amount:.2f})"
        )
    
    # Generate IDs
    transaction_id = generate_transaction_id()
    invoice_no = generate_invoice_number()
    
    # Create payment record
    new_payment = Payment(
        transaction_id=transaction_id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_status=PaymentStatus.PENDING,
        reference_number=payment.reference_number,
        notes=payment.notes
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    # Add invoice_no to response (derived from transaction_id)
    response_dict = {
        **new_payment.__dict__,
        "invoice_no": invoice_no
    }
    
    return response_dict


@router.get("/", response_model=PaymentListResponse)
def get_payments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    booking_id: Optional[int] = Query(None, description="Filter by booking ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all payments with optional filters.
    
    **Filters:**
    - **payment_status**: pending, completed, failed, refunded
    - **payment_method**: cash, credit_card, debit_card, upi, net_banking, wallet
    - **booking_id**: Filter by specific booking
    
    **Pagination:**
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return (max 100)
    """
    # ✅ FIX: Add eager loading of relationships
    query = db.query(Payment).options(
        joinedload(Payment.booking).joinedload(Booking.customer),
        joinedload(Payment.booking).joinedload(Booking.room)
    )
    
    # Apply filters
    if payment_status:
        query = query.filter(Payment.payment_status == payment_status)
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by creation date
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add invoice numbers to responses
    payments_with_invoice = []
    for payment in payments:
        payment_dict = {
            **payment.__dict__,
            "invoice_no": f"INV-{payment.transaction_id}"
        }
        payments_with_invoice.append(payment_dict)
    
    return {
        "total": total,
        "payments": payments_with_invoice
    }


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific payment by ID.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    response_dict = {
        **payment.__dict__,
        "invoice_no": f"INV-{payment.transaction_id}"
    }
    
    return response_dict


@router.get("/transaction/{transaction_id}", response_model=PaymentResponse)
def get_payment_by_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment details by transaction ID.
    
    Useful for payment verification and customer inquiries.
    """
    payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with transaction ID '{transaction_id}' not found"
        )
    
    response_dict = {
        **payment.__dict__,
        "invoice_no": f"INV-{payment.transaction_id}"
    }
    
    return response_dict


@router.patch("/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update payment status (e.g., mark as completed or failed).
    
    **Status Transitions:**
    - PENDING → COMPLETED (when payment is successful)
    - PENDING → FAILED (when payment fails)
    - Any status → REFUNDED (for refunds)
    
    **Updates:**
    - Sets payment_date when marked as COMPLETED
    - Allows updating reference_number and notes
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    # Update payment status
    if payment_update.payment_status:
        payment.payment_status = payment_update.payment_status
        
        # Set payment date when completed
        if payment_update.payment_status == PaymentStatus.COMPLETED and not payment.payment_date:
            payment.payment_date = datetime.now()
    
    # Update reference number if provided
    if payment_update.reference_number is not None:
        payment.reference_number = payment_update.reference_number
    
    # Update notes if provided
    if payment_update.notes is not None:
        payment.notes = payment_update.notes
    
    db.commit()
    db.refresh(payment)
    
    response_dict = {
        **payment.__dict__,
        "invoice_no": f"INV-{payment.transaction_id}"
    }
    
    return response_dict


@router.post("/{payment_id}/refund", response_model=RefundResponse)
def refund_payment(
    payment_id: int,
    refund_request: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Process a payment refund (Admin only).
    
    **Process:**
    1. Validates payment exists and is refundable
    2. Marks payment as REFUNDED
    3. Records refund reason and date
    
    **Business Rules:**
    - Only COMPLETED payments can be refunded
    - Partial refunds not supported (full refund only)
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    if payment.payment_status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed payments can be refunded"
        )
    
    # Update payment to refunded status
    payment.payment_status = PaymentStatus.REFUNDED
    payment.notes = f"REFUNDED: {refund_request.reason}. Original notes: {payment.notes or 'None'}"
    
    db.commit()
    db.refresh(payment)
    
    return RefundResponse(
        payment_id=payment.id,
        transaction_id=payment.transaction_id,
        refund_amount=payment.amount,
        refund_status="success",
        refund_date=datetime.now(),
        message="Payment refunded successfully"
    )


@router.get("/booking/{booking_id}/summary", response_model=PaymentSummary)
def get_booking_payment_summary(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment summary for a specific booking.
    
    Shows total paid, pending, and refunded amounts.
    """
    # Get booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Get all payments for this booking
    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    
    # Calculate totals
    total_paid = sum(p.amount for p in payments if p.payment_status == PaymentStatus.COMPLETED)
    total_pending = sum(p.amount for p in payments if p.payment_status == PaymentStatus.PENDING)
    total_refunded = sum(p.amount for p in payments if p.payment_status == PaymentStatus.REFUNDED)
    
    return PaymentSummary(
        booking_id=booking_id,
        booking_reference=booking.booking_reference,
        total_amount=booking.final_amount,
        total_paid=total_paid,
        total_pending=total_pending,
        total_refunded=total_refunded,
        balance_due=booking.final_amount - total_paid,
        payment_count=len(payments)
    )


@router.get("/invoices/booking/{booking_id}", response_model=InvoiceResponse)
def get_invoice_by_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and retrieve invoice for a booking.
    
    **Invoice Details Include:**
    - Booking information
    - Customer details
    - Room information
    - Itemized charges breakdown
    - Payment information
    - Total amount with tax
    """
    # Get booking with relationships
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Get associated payment
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payment found for booking {booking_id}"
        )
    
    # Build invoice items
    items = [
        InvoiceItemDetail(
            description=f"Room {booking.room.room_number} - {booking.room.room_type.value.title()}",
            quantity=booking.number_of_nights,
            unit_price=booking.room_price,
            amount=booking.total_amount
        )
    ]
    
    # Create invoice response
    invoice = InvoiceResponse(
        invoice_no=f"INV-{payment.transaction_id}",
        invoice_date=payment.created_at,
        booking_id=booking.id,
        booking_reference=booking.booking_reference,
        customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
        customer_email=booking.customer.email,
        customer_phone=booking.customer.phone,
        room_number=booking.room.room_number,
        room_type=booking.room.room_type.value.title(),
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_nights=booking.number_of_nights,
        items=items,
        subtotal=booking.total_amount,
        discount=booking.discount,
        tax=booking.tax,
        total_amount=booking.final_amount,
        payment_status=payment.payment_status.value,
        payment_method=payment.payment_method.value,
        payment_date=payment.payment_date,
        created_at=payment.created_at
    )
    
    return invoice


@router.get("/invoices/payment/{payment_id}", response_model=InvoiceResponse)
def get_invoice_by_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice by payment ID.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    # Use the booking ID to generate invoice
    return get_invoice_by_booking(payment.booking_id, db, current_user)


@router.get("/booking/{booking_id}/history", response_model=PaymentListResponse)
def get_booking_payment_history(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete payment history for a booking.
    
    Shows all payment attempts, including pending, completed, failed, and refunded.
    """
    # Verify booking exists
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Get all payments for this booking
    payments = db.query(Payment).filter(
        Payment.booking_id == booking_id
    ).order_by(Payment.created_at.desc()).all()
    
    # Add invoice numbers to responses
    payments_with_invoice = []
    for payment in payments:
        payment_dict = {
            **payment.__dict__,
            "invoice_no": f"INV-{payment.transaction_id}"
        }
        payments_with_invoice.append(payment_dict)
    
    return {
        "total": len(payments_with_invoice),
        "payments": payments_with_invoice
    }