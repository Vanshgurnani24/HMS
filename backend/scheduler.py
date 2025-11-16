"""
Background Scheduler for HMS
Handles automatic daily tasks like room status updates for bookings.

This can be run as:
1. A cron job (Linux/Unix)
2. Task Scheduler (Windows)
3. Background service with APScheduler
"""

import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.booking import Booking, BookingStatus
from models.room import RoomStatus


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def update_room_status_for_today():
    """
    Automatically set room status to RESERVED for confirmed bookings starting today.
    
    This function:
    1. Finds all CONFIRMED bookings with check_in_date = today
    2. Sets their associated room status to RESERVED
    3. Returns summary of updates
    """
    db = get_db()
    today = date.today()
    
    try:
        # Find all confirmed bookings starting today
        bookings_starting_today = db.query(Booking).filter(
            Booking.check_in_date == today,
            Booking.status == BookingStatus.CONFIRMED
        ).all()
        
        updated_count = 0
        updated_rooms = []
        
        for booking in bookings_starting_today:
            if booking.room.status != RoomStatus.RESERVED:
                booking.room.status = RoomStatus.RESERVED
                updated_count += 1
                updated_rooms.append({
                    "booking_id": booking.id,
                    "booking_reference": booking.booking_reference,
                    "room_number": booking.room.room_number,
                    "room_id": booking.room.id,
                    "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}"
                })
        
        db.commit()
        
        print(f"✅ Room Status Update Summary - {today}")
        print(f"Total bookings starting today: {len(bookings_starting_today)}")
        print(f"Rooms updated to RESERVED: {updated_count}")
        
        if updated_rooms:
            print("\nUpdated Rooms:")
            for room in updated_rooms:
                print(f"  - Room {room['room_number']}: Booking {room['booking_reference']} - {room['customer_name']}")
        
        return {
            "success": True,
            "date": str(today),
            "total_bookings": len(bookings_starting_today),
            "updated_count": updated_count,
            "updated_rooms": updated_rooms
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating room status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


def get_upcoming_checkin_alerts():
    """
    Get list of bookings with check-in scheduled for tomorrow.
    
    This helps staff know which rooms should NOT be allocated
    as they have confirmed bookings starting tomorrow.
    """
    db = get_db()
    tomorrow = date.today() + timedelta(days=1)
    
    try:
        # Find confirmed bookings starting tomorrow
        bookings_tomorrow = db.query(Booking).filter(
            Booking.check_in_date == tomorrow,
            Booking.status == BookingStatus.CONFIRMED
        ).all()
        
        alerts = []
        for booking in bookings_tomorrow:
            alerts.append({
                "booking_reference": booking.booking_reference,
                "room_number": booking.room.room_number,
                "room_type": booking.room.room_type.value,
                "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}",
                "number_of_guests": booking.number_of_guests,
                "special_requests": booking.special_requests
            })
        
        print(f"\n📅 Upcoming Check-in Alerts - {tomorrow}")
        print(f"Total bookings starting tomorrow: {len(alerts)}")
        
        if alerts:
            print("\n⚠️ These rooms should NOT be allocated:")
            for alert in alerts:
                print(f"  - Room {alert['room_number']} ({alert['room_type']}): {alert['customer_name']} - Booking {alert['booking_reference']}")
        else:
            print("No check-ins scheduled for tomorrow.")
        
        return {
            "success": True,
            "date": str(tomorrow),
            "total_alerts": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        print(f"❌ Error fetching alerts: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


def main():
    """Main scheduler function"""
    print("\n" + "="*60)
    print("HMS Background Scheduler - Daily Tasks")
    print("="*60)
    
    # Task 1: Update room status for today's check-ins
    print("\n📋 Task 1: Updating room status for today's confirmed bookings...")
    update_result = update_room_status_for_today()
    
    # Task 2: Get alerts for tomorrow's check-ins
    print("\n📋 Task 2: Checking for tomorrow's check-ins...")
    alert_result = get_upcoming_checkin_alerts()
    
    print("\n" + "="*60)
    print("✅ Scheduler tasks completed!")
    print("="*60 + "\n")
    
    return {
        "update_result": update_result,
        "alert_result": alert_result
    }


if __name__ == "__main__":
    main()