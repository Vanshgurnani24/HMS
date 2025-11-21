"""
Reports and Analytics Router
Provides various reporting endpoints for hotel management analytics.

Day 7 Implementation - Comprehensive Reporting System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import date, datetime, timedelta
from collections import defaultdict

from database import get_db
from models.room import Room, RoomStatus
from models.booking import Booking, BookingStatus
from models.payment import Payment, PaymentMethod, PaymentStatus
from models.customer import Customer
from models.user import User, UserRole
from schemas.report_schema import (
    OccupancyReport,
    RoomStatusCount,
    RoomTypeOccupancy,
    DailyRevenue,
    RevenueReport,
    RevenueByDate,
    PaymentMethodRevenue,
    BookingHistoryReport,
    BookingSummary,
    DashboardSummary,
    QuickStats,
    CustomerBookingStats,
    TopCustomersReport
)
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


# ============================================
# UNIFIED REPORTS ENDPOINT
# ============================================

@router.get("/")
def get_unified_report(
    report_type: str = Query("overview", description="Report type: overview, rooms, bookings, revenue"),
    date_range: str = Query("all", description="Date range: all, today, week, month, year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unified reports endpoint that returns data based on report type and date range.

    **Report Types**:
    - overview: Overall system statistics
    - rooms: Room analysis and occupancy
    - bookings: Booking analysis
    - revenue: Revenue analysis

    **Date Ranges**:
    - all: All time data
    - today: Today's data
    - week: This week's data
    - month: This month's data
    - year: This year's data

    **Access**: All authenticated users
    """
    # Calculate date range
    today = date.today()
    start_date = None
    end_date = today

    if date_range == "today":
        start_date = today
    elif date_range == "week":
        start_date = today - timedelta(days=today.weekday())  # Start of week (Monday)
    elif date_range == "month":
        start_date = today.replace(day=1)  # Start of month
    elif date_range == "year":
        start_date = today.replace(month=1, day=1)  # Start of year
    # else date_range == "all": no start_date filter

    # ============================================
    # OVERVIEW REPORT
    # ============================================
    if report_type == "overview":
        # Room stats
        total_rooms = db.query(Room).filter(Room.is_active == True).count()
        available_rooms = db.query(Room).filter(
            Room.is_active == True,
            Room.status == RoomStatus.AVAILABLE
        ).count()
        occupied_rooms = db.query(Room).filter(
            Room.is_active == True,
            Room.status == RoomStatus.OCCUPIED
        ).count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

        # Customer stats
        customer_query = db.query(Customer)
        if start_date:
            customer_query = customer_query.filter(Customer.created_at >= datetime.combine(start_date, datetime.min.time()))
        total_customers = customer_query.count()

        # Booking stats
        booking_query = db.query(Booking)
        if start_date:
            booking_query = booking_query.filter(
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at <= datetime.combine(end_date, datetime.max.time())
            )

        total_bookings = booking_query.count()
        active_bookings = booking_query.filter(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
        ).count()

        # Revenue stats
        payment_query = db.query(Payment).filter(Payment.payment_status == PaymentStatus.COMPLETED)
        if start_date:
            payment_query = payment_query.filter(
                Payment.payment_date >= datetime.combine(start_date, datetime.min.time()),
                Payment.payment_date <= datetime.combine(end_date, datetime.max.time())
            )

        total_revenue = payment_query.with_entities(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        avg_booking_value = (total_revenue / total_bookings) if total_bookings > 0 else 0

        # Room type distribution
        room_types_data = db.query(
            Room.room_type,
            func.count(Room.id)
        ).filter(Room.is_active == True).group_by(Room.room_type).all()

        room_types = [
            {"name": rt.replace('_', ' ').title(), "value": count}
            for rt, count in room_types_data
        ]

        # Booking status distribution
        booking_status_query = booking_query if start_date else db.query(Booking)
        booking_status_data = booking_status_query.with_entities(
            Booking.status,
            func.count(Booking.id)
        ).group_by(Booking.status).all()

        booking_status = [
            {"name": status.value.replace('_', ' ').title(), "value": count}
            for status, count in booking_status_data
        ]

        # Revenue by month (last 6 months or date range)
        revenue_by_month = []
        if start_date:
            # Calculate months in range
            current_date = start_date
            while current_date <= end_date:
                month_start = datetime.combine(current_date.replace(day=1), datetime.min.time())
                # Get last day of month
                if current_date.month == 12:
                    month_end = datetime.combine(date(current_date.year + 1, 1, 1) - timedelta(days=1), datetime.max.time())
                else:
                    month_end = datetime.combine(date(current_date.year, current_date.month + 1, 1) - timedelta(days=1), datetime.max.time())

                month_revenue = db.query(
                    func.coalesce(func.sum(Payment.amount), 0)
                ).filter(
                    Payment.payment_status == PaymentStatus.COMPLETED,
                    Payment.payment_date >= month_start,
                    Payment.payment_date <= month_end
                ).scalar()

                revenue_by_month.append({
                    "month": current_date.strftime("%b"),
                    "revenue": float(month_revenue)
                })

                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        else:
            # Last 6 months for "all time"
            for i in range(5, -1, -1):
                target_date = today - timedelta(days=i*30)
                month_start = datetime.combine(target_date.replace(day=1), datetime.min.time())
                if target_date.month == 12:
                    month_end = datetime.combine(date(target_date.year + 1, 1, 1) - timedelta(days=1), datetime.max.time())
                else:
                    month_end = datetime.combine(date(target_date.year, target_date.month + 1, 1) - timedelta(days=1), datetime.max.time())

                month_revenue = db.query(
                    func.coalesce(func.sum(Payment.amount), 0)
                ).filter(
                    Payment.payment_status == PaymentStatus.COMPLETED,
                    Payment.payment_date >= month_start,
                    Payment.payment_date <= month_end
                ).scalar()

                revenue_by_month.append({
                    "month": target_date.strftime("%b"),
                    "revenue": float(month_revenue)
                })

        return {
            "report_type": "overview",
            "date_range": date_range,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat(),
            "stats": {
                "total_rooms": total_rooms,
                "available_rooms": available_rooms,
                "occupancy_rate": round(occupancy_rate, 1),
                "total_bookings": total_bookings,
                "active_bookings": active_bookings,
                "total_revenue": float(total_revenue),
                "avg_booking_value": round(float(avg_booking_value), 0),
                "total_customers": total_customers
            },
            "charts": {
                "room_types": room_types,
                "booking_status": booking_status,
                "revenue_by_month": revenue_by_month
            }
        }

    # ============================================
    # ROOM ANALYSIS REPORT
    # ============================================
    elif report_type == "rooms":
        # Get occupancy report data
        total_rooms = db.query(Room).count()
        active_rooms = db.query(Room).filter(Room.is_active == True).count()

        # Status counts
        status_counts = db.query(
            Room.status,
            func.count(Room.id)
        ).filter(Room.is_active == True).group_by(Room.status).all()

        by_status = [
            {"status": status.value, "count": count}
            for status, count in status_counts
        ]

        # Type occupancy
        room_types = db.query(Room.room_type).distinct().all()
        by_type = []

        for (room_type,) in room_types:
            type_stats = db.query(Room).filter(
                Room.room_type == room_type,
                Room.is_active == True
            )

            total = type_stats.count()
            available = type_stats.filter(Room.status == RoomStatus.AVAILABLE).count()
            occupied = type_stats.filter(Room.status == RoomStatus.OCCUPIED).count()
            reserved = type_stats.filter(Room.status == RoomStatus.RESERVED).count()
            maintenance = type_stats.filter(Room.status == RoomStatus.MAINTENANCE).count()

            occupancy_rate = (occupied / total * 100) if total > 0 else 0

            by_type.append({
                "room_type": room_type,
                "total_rooms": total,
                "available": available,
                "occupied": occupied,
                "reserved": reserved,
                "maintenance": maintenance,
                "occupancy_rate": round(occupancy_rate, 2)
            })

        occupied_count = db.query(Room).filter(
            Room.is_active == True,
            Room.status == RoomStatus.OCCUPIED
        ).count()

        overall_occupancy_rate = (occupied_count / active_rooms * 100) if active_rooms > 0 else 0

        return {
            "report_type": "rooms",
            "date_range": date_range,
            "total_rooms": total_rooms,
            "active_rooms": active_rooms,
            "by_status": by_status,
            "by_type": by_type,
            "overall_occupancy_rate": round(overall_occupancy_rate, 2)
        }

    # ============================================
    # BOOKING ANALYSIS REPORT
    # ============================================
    elif report_type == "bookings":
        booking_query = db.query(Booking)
        if start_date:
            booking_query = booking_query.filter(
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at <= datetime.combine(end_date, datetime.max.time())
            )

        total_bookings = booking_query.count()

        # Status breakdown
        status_breakdown = booking_query.with_entities(
            Booking.status,
            func.count(Booking.id)
        ).group_by(Booking.status).all()

        status_data = [
            {"status": status.value, "count": count}
            for status, count in status_breakdown
        ]

        # Average nights and guests
        avg_nights = booking_query.with_entities(
            func.avg(Booking.number_of_nights)
        ).scalar() or 0

        avg_guests = booking_query.with_entities(
            func.avg(Booking.number_of_guests)
        ).scalar() or 0

        # Room type preferences
        room_type_bookings = booking_query.join(Room).with_entities(
            Room.room_type,
            func.count(Booking.id)
        ).group_by(Room.room_type).all()

        room_preferences = [
            {"room_type": rt, "count": count}
            for rt, count in room_type_bookings
        ]

        return {
            "report_type": "bookings",
            "date_range": date_range,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat(),
            "total_bookings": total_bookings,
            "status_breakdown": status_data,
            "avg_nights": round(float(avg_nights), 1),
            "avg_guests": round(float(avg_guests), 1),
            "room_preferences": room_preferences
        }

    # ============================================
    # REVENUE ANALYSIS REPORT
    # ============================================
    elif report_type == "revenue":
        payment_query = db.query(Payment).filter(Payment.payment_status == PaymentStatus.COMPLETED)
        if start_date:
            payment_query = payment_query.filter(
                Payment.payment_date >= datetime.combine(start_date, datetime.min.time()),
                Payment.payment_date <= datetime.combine(end_date, datetime.max.time())
            )

        total_revenue = payment_query.with_entities(
            func.coalesce(func.sum(Payment.amount), 0)
        ).scalar()

        payment_count = payment_query.count()

        # Revenue by payment method
        payment_method_stats = payment_query.with_entities(
            Payment.payment_method,
            func.sum(Payment.amount),
            func.count(Payment.id)
        ).group_by(Payment.payment_method).all()

        by_payment_method = [
            {
                "payment_method": method.value,
                "total_amount": float(total),
                "transaction_count": count
            }
            for method, total, count in payment_method_stats
        ]

        # Daily/Monthly revenue breakdown
        revenue_breakdown = []
        if date_range == "today":
            # Hourly breakdown for today
            for hour in range(24):
                hour_start = datetime.combine(today, datetime.min.time()) + timedelta(hours=hour)
                hour_end = hour_start + timedelta(hours=1)

                hour_revenue = db.query(
                    func.coalesce(func.sum(Payment.amount), 0)
                ).filter(
                    Payment.payment_status == PaymentStatus.COMPLETED,
                    Payment.payment_date >= hour_start,
                    Payment.payment_date < hour_end
                ).scalar()

                revenue_breakdown.append({
                    "period": f"{hour:02d}:00",
                    "revenue": float(hour_revenue)
                })
        else:
            # Daily breakdown
            current_date = start_date if start_date else today - timedelta(days=30)
            while current_date <= end_date:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())

                day_revenue = db.query(
                    func.coalesce(func.sum(Payment.amount), 0)
                ).filter(
                    Payment.payment_status == PaymentStatus.COMPLETED,
                    Payment.payment_date >= day_start,
                    Payment.payment_date <= day_end
                ).scalar()

                revenue_breakdown.append({
                    "period": current_date.strftime("%Y-%m-%d"),
                    "revenue": float(day_revenue)
                })

                current_date += timedelta(days=1)

        avg_transaction_value = (total_revenue / payment_count) if payment_count > 0 else 0

        return {
            "report_type": "revenue",
            "date_range": date_range,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat(),
            "total_revenue": float(total_revenue),
            "payment_count": payment_count,
            "avg_transaction_value": round(float(avg_transaction_value), 2),
            "by_payment_method": by_payment_method,
            "revenue_breakdown": revenue_breakdown
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report_type: {report_type}. Must be one of: overview, rooms, bookings, revenue"
        )


# ============================================
# OCCUPANCY REPORTS
# ============================================

@router.get("/occupancy", response_model=OccupancyReport)
def get_occupancy_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current room occupancy report.
    
    Provides comprehensive statistics on room availability and occupancy:
    - Total rooms and active rooms
    - Breakdown by room status (available, occupied, reserved, maintenance)
    - Breakdown by room type (single, double, suite, deluxe)
    - Overall occupancy rate
    - Rooms available for immediate booking
    
    **Access**: All authenticated users
    """
    # Get total room counts
    total_rooms = db.query(Room).count()
    active_rooms = db.query(Room).filter(Room.is_active == True).count()
    
    # Count by status
    status_counts = db.query(
        Room.status,
        func.count(Room.id)
    ).filter(
        Room.is_active == True
    ).group_by(Room.status).all()
    
    by_status = [
        RoomStatusCount(status=status, count=count)
        for status, count in status_counts
    ]
    
    # Count by type with detailed breakdown
    room_types = db.query(Room.room_type).distinct().all()
    by_type = []
    
    for (room_type,) in room_types:
        type_stats = db.query(Room).filter(
            Room.room_type == room_type,
            Room.is_active == True
        )
        
        total = type_stats.count()
        available = type_stats.filter(Room.status == RoomStatus.AVAILABLE).count()
        occupied = type_stats.filter(Room.status == RoomStatus.OCCUPIED).count()
        reserved = type_stats.filter(Room.status == RoomStatus.RESERVED).count()
        maintenance = type_stats.filter(Room.status == RoomStatus.MAINTENANCE).count()
        
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
        by_type.append(RoomTypeOccupancy(
            room_type=room_type,
            total_rooms=total,
            available=available,
            occupied=occupied,
            reserved=reserved,
            maintenance=maintenance,
            occupancy_rate=round(occupancy_rate, 2)
        ))
    
    # Calculate overall occupancy rate
    occupied_count = db.query(Room).filter(
        Room.is_active == True,
        Room.status == RoomStatus.OCCUPIED
    ).count()
    
    overall_occupancy_rate = (occupied_count / active_rooms * 100) if active_rooms > 0 else 0
    
    # Available for booking
    available_for_booking = db.query(Room).filter(
        Room.is_active == True,
        Room.status == RoomStatus.AVAILABLE
    ).count()
    
    return OccupancyReport(
        report_date=datetime.utcnow(),
        total_rooms=total_rooms,
        active_rooms=active_rooms,
        by_status=by_status,
        by_type=by_type,
        overall_occupancy_rate=round(overall_occupancy_rate, 2),
        available_for_booking=available_for_booking
    )


@router.get("/occupancy/type/{room_type}", response_model=RoomTypeOccupancy)
def get_occupancy_by_type(
    room_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get occupancy report for a specific room type.
    
    **Parameters**:
    - **room_type**: single, double, suite, or deluxe
    
    **Access**: All authenticated users
    """
    type_stats = db.query(Room).filter(
        Room.room_type == room_type,
        Room.is_active == True
    )
    
    total = type_stats.count()
    
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active rooms found for type '{room_type}'"
        )
    
    available = type_stats.filter(Room.status == RoomStatus.AVAILABLE).count()
    occupied = type_stats.filter(Room.status == RoomStatus.OCCUPIED).count()
    reserved = type_stats.filter(Room.status == RoomStatus.RESERVED).count()
    maintenance = type_stats.filter(Room.status == RoomStatus.MAINTENANCE).count()
    
    occupancy_rate = (occupied / total * 100) if total > 0 else 0
    
    return RoomTypeOccupancy(
        room_type=room_type,
        total_rooms=total,
        available=available,
        occupied=occupied,
        reserved=reserved,
        maintenance=maintenance,
        occupancy_rate=round(occupancy_rate, 2)
    )


# ============================================
# REVENUE REPORTS
# ============================================

@router.get("/revenue/daily", response_model=DailyRevenue)
def get_daily_revenue(
    target_date: date = Query(..., description="Date for revenue report (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Get revenue report for a specific date.
    
    Includes:
    - Total revenue for the day
    - Count of completed, pending, and failed payments
    - Refunded amount
    - Net revenue (total - refunds)
    
    **Parameters**:
    - **target_date**: Date in YYYY-MM-DD format
    
    **Access**: Admin and Staff only
    """
    # Query payments for the specific date
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    # Total completed revenue
    completed_revenue = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        Payment.payment_date >= start_datetime,
        Payment.payment_date <= end_datetime
    ).scalar()
    
    # Refunded amount
    refunded_amount = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_status == PaymentStatus.REFUNDED,
        Payment.updated_at >= start_datetime,
        Payment.updated_at <= end_datetime
    ).scalar()
    
    # Count by status
    completed_count = db.query(Payment).filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        Payment.payment_date >= start_datetime,
        Payment.payment_date <= end_datetime
    ).count()
    
    pending_count = db.query(Payment).filter(
        Payment.payment_status == PaymentStatus.PENDING,
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime
    ).count()
    
    failed_count = db.query(Payment).filter(
        Payment.payment_status == PaymentStatus.FAILED,
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime
    ).count()
    
    net_revenue = completed_revenue - refunded_amount
    
    return DailyRevenue(
        date=target_date,
        total_revenue=float(completed_revenue),
        completed_payments=completed_count,
        pending_payments=pending_count,
        failed_payments=failed_count,
        refunded_amount=float(refunded_amount),
        net_revenue=float(net_revenue)
    )


@router.get("/revenue/range", response_model=RevenueReport)
def get_revenue_report(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Get comprehensive revenue report for a date range.
    
    Includes:
    - Total revenue and booking count
    - Average booking value
    - Breakdown by payment method
    - Daily revenue breakdown
    
    **Parameters**:
    - **start_date**: Start date in YYYY-MM-DD format
    - **end_date**: End date in YYYY-MM-DD format
    
    **Access**: Admin and Staff only
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Total revenue from completed payments
    total_revenue = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        Payment.payment_date >= start_datetime,
        Payment.payment_date <= end_datetime
    ).scalar()
    
    # Total bookings in range
    total_bookings = db.query(Booking).filter(
        Booking.created_at >= start_datetime,
        Booking.created_at <= end_datetime
    ).count()
    
    # Average booking value
    average_booking_value = (total_revenue / total_bookings) if total_bookings > 0 else 0
    
    # Revenue by payment method
    payment_method_stats = db.query(
        Payment.payment_method,
        func.sum(Payment.amount),
        func.count(Payment.id)
    ).filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        Payment.payment_date >= start_datetime,
        Payment.payment_date <= end_datetime
    ).group_by(Payment.payment_method).all()
    
    by_payment_method = [
        PaymentMethodRevenue(
            payment_method=method,
            total_amount=float(total),
            transaction_count=count
        )
        for method, total, count in payment_method_stats
    ]
    
    # Daily breakdown
    daily_breakdown = []
    current_date = start_date
    
    while current_date <= end_date:
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())
        
        day_revenue = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_status == PaymentStatus.COMPLETED,
            Payment.payment_date >= day_start,
            Payment.payment_date <= day_end
        ).scalar()
        
        day_bookings = db.query(Booking).filter(
            Booking.created_at >= day_start,
            Booking.created_at <= day_end
        ).count()
        
        daily_breakdown.append(RevenueByDate(
            date=current_date,
            revenue=float(day_revenue),
            booking_count=day_bookings
        ))
        
        current_date += timedelta(days=1)
    
    return RevenueReport(
        start_date=start_date,
        end_date=end_date,
        total_revenue=float(total_revenue),
        total_bookings=total_bookings,
        average_booking_value=round(float(average_booking_value), 2),
        by_payment_method=by_payment_method,
        daily_breakdown=daily_breakdown
    )


# ============================================
# BOOKING HISTORY REPORTS
# ============================================

@router.get("/bookings/history", response_model=BookingHistoryReport)
def get_booking_history(
    start_date: Optional[date] = Query(None, description="Filter by check-in date start"),
    end_date: Optional[date] = Query(None, description="Filter by check-in date end"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking history with various filters.
    
    **Filters**:
    - **start_date**: Filter bookings with check-in >= this date
    - **end_date**: Filter bookings with check-in <= this date
    - **status**: Filter by booking status
    - **customer_id**: Filter by specific customer
    - **room_id**: Filter by specific room
    
    **Pagination**:
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return (max 500)
    
    **Access**: All authenticated users
    """
    query = db.query(Booking)
    
    # Apply filters
    if start_date:
        query = query.filter(Booking.check_in_date >= start_date)
    if end_date:
        query = query.filter(Booking.check_in_date <= end_date)
    if status:
        query = query.filter(Booking.status == status)
    if customer_id:
        query = query.filter(Booking.customer_id == customer_id)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    
    # Get total count
    total_bookings = query.count()
    
    # Apply pagination and get bookings
    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to summaries
    booking_summaries = []
    for booking in bookings:
        booking_summaries.append(BookingSummary(
            id=booking.id,
            booking_reference=booking.booking_reference,
            customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
            customer_email=booking.customer.email,
            room_number=booking.room.room_number,
            room_type=booking.room.room_type,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            number_of_nights=booking.number_of_nights,
            number_of_guests=booking.number_of_guests,
            total_amount=booking.total_amount,
            final_amount=booking.final_amount,
            status=booking.status,
            created_at=booking.created_at
        ))
    
    # Status breakdown
    all_bookings = query.all()
    status_breakdown = defaultdict(int)
    for booking in all_bookings:
        status_breakdown[booking.status.value] += 1
    
    return BookingHistoryReport(
        start_date=start_date,
        end_date=end_date,
        total_bookings=total_bookings,
        bookings=booking_summaries,
        status_breakdown=dict(status_breakdown)
    )


@router.get("/bookings/upcoming", response_model=BookingHistoryReport)
def get_upcoming_bookings(
    days: int = Query(7, ge=1, le=90, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upcoming bookings for the next N days.
    
    **Parameters**:
    - **days**: Number of days to look ahead (1-90, default: 7)
    
    Shows bookings with check-in dates in the specified range.
    
    **Access**: All authenticated users
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    bookings = db.query(Booking).filter(
        Booking.check_in_date >= today,
        Booking.check_in_date <= end_date,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).order_by(Booking.check_in_date).all()
    
    booking_summaries = []
    for booking in bookings:
        booking_summaries.append(BookingSummary(
            id=booking.id,
            booking_reference=booking.booking_reference,
            customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
            customer_email=booking.customer.email,
            room_number=booking.room.room_number,
            room_type=booking.room.room_type,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            number_of_nights=booking.number_of_nights,
            number_of_guests=booking.number_of_guests,
            total_amount=booking.total_amount,
            final_amount=booking.final_amount,
            status=booking.status,
            created_at=booking.created_at
        ))
    
    status_breakdown = defaultdict(int)
    for booking in bookings:
        status_breakdown[booking.status.value] += 1
    
    return BookingHistoryReport(
        start_date=today,
        end_date=end_date,
        total_bookings=len(bookings),
        bookings=booking_summaries,
        status_breakdown=dict(status_breakdown)
    )


# ============================================
# DASHBOARD SUMMARY
# ============================================

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Get comprehensive dashboard summary with key metrics.
    
    Includes:
    - Quick stats (rooms, customers, bookings, revenue)
    - Overall occupancy rate
    - Recent bookings (last 10)
    - Revenue trend (last 7 days)
    
    **Access**: Admin and Staff only
    """
    # Quick stats
    total_rooms = db.query(Room).filter(Room.is_active == True).count()
    occupied_rooms = db.query(Room).filter(
        Room.is_active == True,
        Room.status == RoomStatus.OCCUPIED
    ).count()
    available_rooms = db.query(Room).filter(
        Room.is_active == True,
        Room.status == RoomStatus.AVAILABLE
    ).count()
    
    total_customers = db.query(Customer).count()
    
    active_bookings = db.query(Booking).filter(
        Booking.status.in_([
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN,
            BookingStatus.PENDING
        ])
    ).count()
    
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    todays_checkins = db.query(Booking).filter(
        Booking.check_in_date == today,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).count()
    
    todays_checkouts = db.query(Booking).filter(
        Booking.check_out_date == today,
        Booking.status == BookingStatus.CHECKED_IN
    ).count()
    
    todays_revenue = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_status == PaymentStatus.COMPLETED,
        Payment.payment_date >= today_start,
        Payment.payment_date <= today_end
    ).scalar()
    
    pending_payments_count = db.query(Payment).filter(
        Payment.payment_status == PaymentStatus.PENDING
    ).count()
    
    pending_payment_amount = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_status == PaymentStatus.PENDING
    ).scalar()
    
    quick_stats = QuickStats(
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        available_rooms=available_rooms,
        total_customers=total_customers,
        active_bookings=active_bookings,
        todays_checkins=todays_checkins,
        todays_checkouts=todays_checkouts,
        todays_revenue=float(todays_revenue),
        pending_payments=pending_payments_count,
        pending_payment_amount=float(pending_payment_amount)
    )
    
    # Occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Recent bookings (last 10)
    recent_bookings_data = db.query(Booking).order_by(
        Booking.created_at.desc()
    ).limit(10).all()
    
    recent_bookings = []
    for booking in recent_bookings_data:
        recent_bookings.append(BookingSummary(
            id=booking.id,
            booking_reference=booking.booking_reference,
            customer_name=f"{booking.customer.first_name} {booking.customer.last_name}",
            customer_email=booking.customer.email,
            room_number=booking.room.room_number,
            room_type=booking.room.room_type,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            number_of_nights=booking.number_of_nights,
            number_of_guests=booking.number_of_guests,
            total_amount=booking.total_amount,
            final_amount=booking.final_amount,
            status=booking.status,
            created_at=booking.created_at
        ))
    
    # Revenue trend (last 7 days)
    revenue_trend = []
    for i in range(6, -1, -1):  # Last 7 days
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_revenue = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_status == PaymentStatus.COMPLETED,
            Payment.payment_date >= day_start,
            Payment.payment_date <= day_end
        ).scalar()
        
        day_bookings = db.query(Booking).filter(
            Booking.created_at >= day_start,
            Booking.created_at <= day_end
        ).count()
        
        revenue_trend.append(RevenueByDate(
            date=day,
            revenue=float(day_revenue),
            booking_count=day_bookings
        ))
    
    return DashboardSummary(
        generated_at=datetime.utcnow(),
        quick_stats=quick_stats,
        occupancy_rate=round(occupancy_rate, 2),
        recent_bookings=recent_bookings,
        revenue_trend=revenue_trend
    )


# ============================================
# CUSTOMER ANALYTICS
# ============================================

@router.get("/customers/top", response_model=TopCustomersReport)
def get_top_customers(
    report_type: str = Query(
        "by_revenue",
        regex="^(by_revenue|by_bookings)$",
        description="Sort by 'by_revenue' or 'by_bookings'"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of customers to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Get top customers by total revenue or number of bookings.
    
    **Parameters**:
    - **report_type**: "by_revenue" or "by_bookings"
    - **limit**: Number of top customers to return (1-100, default: 10)
    
    **Access**: Admin and Staff only
    """
    # Get all customers with their booking stats
    customers = db.query(Customer).all()
    
    customer_stats = []
    
    for customer in customers:
        bookings = customer.bookings
        
        if not bookings:
            continue
        
        total_bookings = len(bookings)
        completed_bookings = len([b for b in bookings if b.status == BookingStatus.CHECKED_OUT])
        cancelled_bookings = len([b for b in bookings if b.status == BookingStatus.CANCELLED])
        total_spent = sum(b.final_amount for b in bookings if b.status != BookingStatus.CANCELLED)
        average_booking_value = total_spent / total_bookings if total_bookings > 0 else 0
        
        # Get last booking date
        last_booking = max(bookings, key=lambda b: b.created_at) if bookings else None
        last_booking_date = last_booking.check_in_date if last_booking else None
        
        customer_stats.append(CustomerBookingStats(
            customer_id=customer.id,
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_email=customer.email,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_spent=round(total_spent, 2),
            average_booking_value=round(average_booking_value, 2),
            last_booking_date=last_booking_date
        ))
    
    # Sort based on report type
    if report_type == "by_revenue":
        customer_stats.sort(key=lambda x: x.total_spent, reverse=True)
    else:  # by_bookings
        customer_stats.sort(key=lambda x: x.total_bookings, reverse=True)
    
    # Limit results
    top_customers = customer_stats[:limit]
    
    return TopCustomersReport(
        report_type=report_type,
        customers=top_customers
    )