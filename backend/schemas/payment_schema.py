"""
Payment and Billing Pydantic schemas for request/response validation.
Handles payment processing, invoice generation, and billing data.

FIXED VERSION - Added nested booking object with customer and room to PaymentResponse
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from models.payment import PaymentMethod, PaymentStatus


# Nested objects for payment response
class CustomerNestedInPayment(BaseModel):
    """Nested customer data"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    
    class Config:
        from_attributes = True


class RoomNestedInPayment(BaseModel):
    """Nested room data"""
    id: int
    room_number: str
    room_type: str
    
    class Config:
        from_attributes = True


class BookingNestedInPayment(BaseModel):
    """Nested booking data in payment response"""
    id: int
    booking_reference: str
    customer_id: int
    room_id: int
    check_in_date: date
    check_out_date: date
    final_amount: float
    status: str
    
    # Nested customer and room in booking
    customer: Optional[CustomerNestedInPayment] = None
    room: Optional[RoomNestedInPayment] = None
    
    class Config:
        from_attributes = True


# Payment Schemas
class PaymentBase(BaseModel):
    booking_id: int = Field(..., gt=0, description="Booking ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference_number: Optional[str] = Field(None, description="Bank/UPI reference number")
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    pass


class PaymentUpdate(BaseModel):
    """Schema for updating payment details"""
    payment_status: Optional[PaymentStatus] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: int
    transaction_id: str
    invoice_no: str  # Invoice number
    payment_status: PaymentStatus
    payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # ✅ FIX: Add nested booking object
    booking: Optional[BookingNestedInPayment] = None
    
    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Schema for paginated payment list"""
    total: int
    payments: list[PaymentResponse]


# Invoice Schemas
class InvoiceItemDetail(BaseModel):
    """Schema for invoice line item"""
    description: str
    number_of_nights: int
    price_per_night: float
    amount: float


class PaymentBreakdownItem(BaseModel):
    """Schema for payment breakdown in receipt"""
    payment_date: datetime
    amount: float
    payment_method: str
    transaction_id: str


class InvoiceResponse(BaseModel):
    """Schema for complete invoice"""
    # Invoice Details
    invoice_no: str
    invoice_date: datetime
    booking_id: int
    
    # Booking Details
    booking_reference: str
    check_in_date: date
    check_out_date: date
    number_of_nights: int
    
    # Customer Details
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: Optional[str] = None
    
    # Room Details
    room_number: str
    room_type: str
    
    # Invoice Items
    items: list[InvoiceItemDetail]
    
    # Amounts
    subtotal: float
    discount: float
    tax: float
    total_amount: float
    
    # Payment Info
    payment_status: str
    payment_method: str
    payment_date: Optional[datetime] = None
    created_at: datetime

    # Payment History Breakdown
    payment_history: list[PaymentBreakdownItem] = []


class PaymentSummary(BaseModel):
    """Payment summary for a booking"""
    booking_id: int
    booking_reference: str
    total_amount: float
    total_paid: float
    total_pending: float
    total_refunded: float
    balance_due: float
    payment_count: int


class RefundRequest(BaseModel):
    """Request to refund a payment"""
    reason: str = Field(..., min_length=10, description="Reason for refund")


class RefundResponse(BaseModel):
    """Response for refund operation"""
    payment_id: int
    transaction_id: str
    refund_amount: float
    refund_status: str
    refund_date: datetime
    message: str