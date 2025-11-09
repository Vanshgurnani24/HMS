"""
Payment and Billing Pydantic schemas for request/response validation.
Handles payment processing, invoice generation, and billing data.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from models.payment import PaymentMethod, PaymentStatus


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
    quantity: int
    unit_price: float
    amount: float


class InvoiceResponse(BaseModel):
    """Schema for complete invoice"""
    # Invoice Details
    invoice_no: str
    invoice_date: datetime
    
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
    
    # Payment Details
    payment_status: PaymentStatus
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    
    # Additional Info
    special_requests: Optional[str] = None
    notes: Optional[str] = None


class PaymentSummary(BaseModel):
    """Schema for payment summary statistics"""
    total_payments: int
    total_amount: float
    completed_payments: int
    completed_amount: float
    pending_payments: int
    pending_amount: float
    failed_payments: int
    failed_amount: float
    payment_methods: dict  # {"cash": count, "card": count, ...}


class RefundRequest(BaseModel):
    """Schema for refund request"""
    payment_id: int
    refund_amount: float = Field(..., gt=0)
    reason: str
    
    
class RefundResponse(BaseModel):
    """Schema for refund response"""
    payment_id: int
    original_amount: float
    refund_amount: float
    refund_status: PaymentStatus
    refund_date: datetime
    reason: str