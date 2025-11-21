"""
Improved Background Scheduler for HMS
Handles automatic daily tasks with startup check for missed executions.

This version:
1. Checks on startup if today's tasks have been run
2. Runs tasks immediately if missed
3. Schedules for next execution
"""

import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.booking import Booking, BookingStatus
from models.room import RoomStatus


# Track last execution in a simple file
LAST_RUN_FILE = Path(__file__).parent / ".scheduler_last_run"


def get_last_run_date():
    """Get the date when scheduler last ran"""
    try:
        if LAST_RUN_FILE.exists():
            with open(LAST_RUN_FILE, 'r') as f:
                date_str = f.read().strip()
                return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception as e:
        print(f"⚠️  Could not read last run date: {e}")
    return None


def save_last_run_date(run_date=None):
    """Save the date when scheduler ran"""
    if run_date is None:
        run_date = date.today()
    try:
        with open(LAST_RUN_FILE, 'w') as f:
            f.write(run_date.strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"⚠️  Could not save last run date: {e}")


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
        else:
            print("No rooms needed status update")
        
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
                "room_type": booking.room.room_type,
                "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}",
                "number_of_guests": booking.number_of_guests,
                "special_requests": booking.special_requests
            })
        
        print(f"\n📅 Upcoming Check-in Alerts - {tomorrow}")
        print(f"Total bookings starting tomorrow: {len(alerts)}")
        
        if alerts:
            print("\n⚠️  These rooms should NOT be allocated:")
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


def should_run_today():
    """
    Check if scheduler should run today.
    Returns True if:
    1. Never run before, OR
    2. Last run was not today
    """
    last_run = get_last_run_date()
    today = date.today()
    
    if last_run is None:
        print(f"📋 No previous run recorded. Will run now.")
        return True
    
    if last_run < today:
        print(f"📋 Last run was on {last_run}. Today is {today}. Will run now.")
        return True
    
    print(f"✓ Already ran today ({today}). Skipping.")
    return False


def run_daily_tasks():
    """
    Run daily tasks with duplicate prevention.
    Only runs once per day, even if called multiple times.
    """
    print("\n" + "="*60)
    print(f"HMS Background Scheduler - {datetime.now()}")
    print("="*60)
    
    # Check if we should run today
    if not should_run_today():
        print("\n✓ Daily tasks already completed for today.")
        print("="*60 + "\n")
        return {
            "skipped": True,
            "message": "Already ran today",
            "last_run": str(get_last_run_date())
        }
    
    # Task 1: Update room status for today's check-ins
    print("\n📋 Task 1: Updating room status for today's confirmed bookings...")
    update_result = update_room_status_for_today()
    
    # Task 2: Get alerts for tomorrow's check-ins
    print("\n📋 Task 2: Checking for tomorrow's check-ins...")
    alert_result = get_upcoming_checkin_alerts()
    
    # Save execution date
    save_last_run_date()
    
    print("\n" + "="*60)
    print("✅ Scheduler tasks completed!")
    print("="*60 + "\n")
    
    return {
        "executed": True,
        "update_result": update_result,
        "alert_result": alert_result,
        "execution_time": str(datetime.now())
    }


def main():
    """Main scheduler function"""
    return run_daily_tasks()


if __name__ == "__main__":
    main()