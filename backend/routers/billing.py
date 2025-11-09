"""
Billing and Payment Management Router
Handles payment processing, invoice generation, and billing operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
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

router = APIRouter(prefix="/billing", tags=["Billing & Payment Management"])


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


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
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
    
    # Store invoice number in notes or add invoice_no field
    # For now, we'll use transaction_id as invoice reference
    # In production, you might add an invoice_no column to Payment model
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    # Add invoice_no to response (derived from transaction_id)
    response_dict = {
        **new_payment.__dict__,
        "invoice_no": invoice_no
    }
    
    return response_dict


@router.get("/payments", response_model=PaymentListResponse)
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
    query = db.query(Payment)
    
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


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
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


@router.get("/payments/transaction/{transaction_id}", response_model=PaymentResponse)
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


@router.patch("/payments/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update payment status (mark as completed, failed, or refunded).
    
    **Status Flow:**
    - PENDING → COMPLETED (payment successful)
    - PENDING → FAILED (payment failed)
    - COMPLETED → REFUNDED (refund processed)
    
    **Automatic Actions:**
    - COMPLETED: Sets payment_date to current timestamp
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    # Update status
    if payment_update.payment_status:
        payment.payment_status = payment_update.payment_status
        
        # Set payment date when marked as completed
        if payment_update.payment_status == PaymentStatus.COMPLETED and not payment.payment_date:
            payment.payment_date = datetime.utcnow()
    
    # Update other fields
    if payment_update.reference_number:
        payment.reference_number = payment_update.reference_number
    if payment_update.notes:
        payment.notes = payment_update.notes
    
    db.commit()
    db.refresh(payment)
    
    response_dict = {
        **payment.__dict__,
        "invoice_no": f"INV-{payment.transaction_id}"
    }
    
    return response_dict


@router.get("/invoices/booking/{booking_id}", response_model=InvoiceResponse)
def get_invoice_by_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and fetch complete invoice for a booking.
    
    **Invoice Includes:**
    - Invoice number (auto-generated)
    - Customer details
    - Room details
    - Booking dates and nights
    - Itemized charges
    - Payment information
    - Tax and discount breakdown
    
    **Invoice Format:** INV-yyyyMMddHHmmss
    """
    # Get booking with related data
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Get payment information
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    
    # Generate invoice number
    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Build invoice items
    items = []
    
    # Room charges
    items.append(InvoiceItemDetail(
        description=f"Room Charges - {booking.room.room_type.value.title()} Room ({booking.room.room_number})",
        quantity=booking.number_of_nights,
        unit_price=booking.room_price,
        amount=booking.total_amount
    ))
    
    # Build complete invoice
    invoice = InvoiceResponse(
        # Invoice Details
        invoice_no=invoice_no,
        invoice_date=datetime.utcnow(),
        
        # Booking Details
        booking_reference=booking.booking_reference,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_nights=booking.number_of_nights,
        
        # Customer Details
        customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
        customer_email=booking.customer.email,
        customer_phone=booking.customer.phone,
        customer_address=booking.customer.address,
        
        # Room Details
        room_number=booking.room.room_number,
        room_type=booking.room.room_type.value,
        
        # Invoice Items
        items=items,
        
        # Amounts
        subtotal=booking.total_amount - booking.discount,
        discount=booking.discount,
        tax=booking.tax,
        total_amount=booking.final_amount,
        
        # Payment Details
        payment_status=payment.payment_status if payment else PaymentStatus.PENDING,
        payment_method=payment.payment_method.value if payment else None,
        payment_date=payment.payment_date if payment else None,
        transaction_id=payment.transaction_id if payment else None,
        
        # Additional Info
        special_requests=booking.special_requests,
        notes=payment.notes if payment else None
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


@router.get("/payments/booking/{booking_id}/history", response_model=PaymentListResponse)
def get_booking_payment_history(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete payment history for a booking.
    
    Useful for tracking multiple payment attempts or partial payments.
    """
    # Validate booking exists
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
    
    payments_with_invoice = []
    for payment in payments:
        payment_dict = {
            **payment.__dict__,
            "invoice_no": f"INV-{payment.transaction_id}"
        }
        payments_with_invoice.append(payment_dict)
    
    return {
        "total": len(payments),
        "payments": payments_with_invoice
    }


@router.get("/summary", response_model=PaymentSummary)
def get_payment_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Get payment summary statistics (Admin only).
    
    **Metrics Include:**
    - Total payments count and amount
    - Completed payments count and amount
    - Pending payments count and amount
    - Failed payments count and amount
    - Payment method distribution
    
    **Filters:**
    - **start_date**: Filter from date (YYYY-MM-DD)
    - **end_date**: Filter to date (YYYY-MM-DD)
    """
    query = db.query(Payment)
    
    # Apply date filters
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    # Get all payments
    all_payments = query.all()
    
    # Calculate summary statistics
    total_payments = len(all_payments)
    total_amount = sum(p.amount for p in all_payments)
    
    completed = [p for p in all_payments if p.payment_status == PaymentStatus.COMPLETED]
    completed_payments = len(completed)
    completed_amount = sum(p.amount for p in completed)
    
    pending = [p for p in all_payments if p.payment_status == PaymentStatus.PENDING]
    pending_payments = len(pending)
    pending_amount = sum(p.amount for p in pending)
    
    failed = [p for p in all_payments if p.payment_status == PaymentStatus.FAILED]
    failed_payments = len(failed)
    failed_amount = sum(p.amount for p in failed)
    
    # Payment method distribution
    payment_methods = {}
    for payment in all_payments:
        method = payment.payment_method.value
        payment_methods[method] = payment_methods.get(method, 0) + 1
    
    return PaymentSummary(
        total_payments=total_payments,
        total_amount=round(total_amount, 2),
        completed_payments=completed_payments,
        completed_amount=round(completed_amount, 2),
        pending_payments=pending_payments,
        pending_amount=round(pending_amount, 2),
        failed_payments=failed_payments,
        failed_amount=round(failed_amount, 2),
        payment_methods=payment_methods
    )


@router.post("/refund", response_model=RefundResponse)
def process_refund(
    refund_request: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Process refund for a payment (Admin only).
    
    **Business Rules:**
    - Can only refund COMPLETED payments
    - Refund amount cannot exceed original payment amount
    - Payment status changes to REFUNDED
    - Original payment record is preserved
    
    **Note:** In production, integrate with payment gateway for actual refund processing.
    """
    # Get payment
    payment = db.query(Payment).filter(Payment.id == refund_request.payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {refund_request.payment_id} not found"
        )
    
    # Validate payment can be refunded
    if payment.payment_status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only refund COMPLETED payments. Current status: {payment.payment_status.value}"
        )
    
    # Validate refund amount
    if refund_request.refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund amount (${refund_request.refund_amount:.2f}) cannot exceed payment amount (${payment.amount:.2f})"
        )
    
    # Process refund
    payment.payment_status = PaymentStatus.REFUNDED
    payment.notes = f"REFUND: {refund_request.reason}. Original notes: {payment.notes or 'N/A'}"
    
    db.commit()
    db.refresh(payment)
    
    return RefundResponse(
        payment_id=payment.id,
        original_amount=payment.amount,
        refund_amount=refund_request.refund_amount,
        refund_status=PaymentStatus.REFUNDED,
        refund_date=datetime.utcnow(),
        reason=refund_request.reason
    )


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete a payment record (Admin only).
    
    **Warning:** This permanently deletes the payment record.
    Consider using refund functionality instead for completed payments.
    
    **Use Cases:**
    - Removing duplicate payment entries
    - Correcting data entry errors
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )
    
    # Prevent deletion of completed payments (use refund instead)
    if payment.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete COMPLETED payment. Use refund functionality instead."
        )
    
    db.delete(payment)
    db.commit()
    
    return None