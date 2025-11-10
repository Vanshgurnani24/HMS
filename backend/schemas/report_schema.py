"""
Report Schemas for Hotel Management System
Pydantic schemas for various analytics and reporting endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from models.room import RoomStatus, RoomType
from models.booking import BookingStatus
from models.payment import PaymentMethod, PaymentStatus


# ============================================
# OCCUPANCY REPORT SCHEMAS
# ============================================

class RoomStatusCount(BaseModel):
    """Count of rooms by status"""
    status: RoomStatus
    count: int


class RoomTypeOccupancy(BaseModel):
    """Occupancy statistics by room type"""
    room_type: RoomType
    total_rooms: int
    available: int
    occupied: int
    reserved: int
    maintenance: int
    occupancy_rate: float = Field(..., description="Percentage of occupied rooms")


class OccupancyReport(BaseModel):
    """Complete occupancy report"""
    report_date: datetime
    total_rooms: int
    active_rooms: int
    by_status: List[RoomStatusCount]
    by_type: List[RoomTypeOccupancy]
    overall_occupancy_rate: float
    available_for_booking: int


# ============================================
# REVENUE REPORT SCHEMAS
# ============================================

class PaymentMethodRevenue(BaseModel):
    """Revenue breakdown by payment method"""
    payment_method: PaymentMethod
    total_amount: float
    transaction_count: int


class DailyRevenue(BaseModel):
    """Revenue for a specific date"""
    date: date
    total_revenue: float
    completed_payments: int
    pending_payments: int
    failed_payments: int
    refunded_amount: float
    net_revenue: float


class RevenueByDate(BaseModel):
    """Revenue data point for a specific date"""
    date: date
    revenue: float
    booking_count: int


class RevenueReport(BaseModel):
    """Complete revenue report for a date range"""
    start_date: date
    end_date: date
    total_revenue: float
    total_bookings: int
    average_booking_value: float
    by_payment_method: List[PaymentMethodRevenue]
    daily_breakdown: List[RevenueByDate]


# ============================================
# BOOKING HISTORY SCHEMAS
# ============================================

class BookingSummary(BaseModel):
    """Summary information for a booking"""
    id: int
    booking_reference: str
    customer_name: str
    customer_email: str
    room_number: str
    room_type: RoomType
    check_in_date: date
    check_out_date: date
    number_of_nights: int
    number_of_guests: int
    total_amount: float
    final_amount: float
    status: BookingStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingHistoryReport(BaseModel):
    """Booking history report with filters"""
    start_date: Optional[date]
    end_date: Optional[date]
    total_bookings: int
    bookings: List[BookingSummary]
    status_breakdown: dict = Field(..., description="Count of bookings by status")


# ============================================
# DASHBOARD SUMMARY SCHEMAS
# ============================================

class QuickStats(BaseModel):
    """Quick statistics for dashboard"""
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    total_customers: int
    active_bookings: int
    todays_checkins: int
    todays_checkouts: int
    todays_revenue: float
    pending_payments: int
    pending_payment_amount: float


class DashboardSummary(BaseModel):
    """Complete dashboard summary"""
    generated_at: datetime
    quick_stats: QuickStats
    occupancy_rate: float
    recent_bookings: List[BookingSummary]
    revenue_trend: List[RevenueByDate]


# ============================================
# CUSTOMER ANALYTICS SCHEMAS
# ============================================

class CustomerBookingStats(BaseModel):
    """Booking statistics for a customer"""
    customer_id: int
    customer_name: str
    customer_email: str
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    total_spent: float
    average_booking_value: float
    last_booking_date: Optional[date]


class TopCustomersReport(BaseModel):
    """Report of top customers by bookings or revenue"""
    report_type: str = Field(..., description="by_bookings or by_revenue")
    customers: List[CustomerBookingStats]