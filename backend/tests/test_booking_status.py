#!/usr/bin/env python3
"""
Hotel Management System - Booking Status Management Test Script
Tests booking status updates, check-in, check-out, and cancellation.
"""

import requests
import json
from datetime import date, timedelta

# =========================
# CONFIGURATION
# =========================
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin@123"


def login():
    """Login and return JWT token."""
    print("\n📝 Logging in...")
    
    login_data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        return token
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        return None


def list_all_bookings(token, status=None):
    """List all bookings."""
    print("\n📋 Fetching bookings...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if status:
        params["status"] = status
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✅ Found {data['total']} booking(s)")
        
        if data["bookings"]:
            print("\n" + "=" * 120)
            print(f"{'ID':<5} {'Reference':<20} {'Customer':<8} {'Room':<6} {'Check-in':<12} {'Check-out':<12} {'Status':<12} {'Amount':<10}")
            print("=" * 120)
            for booking in data["bookings"]:
                print(f"{booking['id']:<5} {booking['booking_reference']:<20} "
                      f"{booking['customer_id']:<8} {booking['room_id']:<6} "
                      f"{booking['check_in_date']:<12} {booking['check_out_date']:<12} "
                      f"{booking['status']:<12} ${booking['final_amount']:<9.2f}")
            print("=" * 120)
        
        return data["bookings"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch bookings: {e}")
        return []


def get_booking_details(token, booking_id):
    """Get detailed booking information."""
    print(f"\n🔍 Fetching booking ID {booking_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/{booking_id}", headers=headers)
        response.raise_for_status()
        booking = response.json()
        
        print("\n✅ Booking found!")
        print("\n" + "=" * 80)
        print("BOOKING DETAILS")
        print("=" * 80)
        print(f"Booking ID: {booking['id']}")
        print(f"Reference: {booking['booking_reference']}")
        print(f"Customer: {booking['customer_name']}")
        print(f"Email: {booking['customer_email']}")
        print(f"Phone: {booking['customer_phone']}")
        print(f"Room: {booking['room_number']} ({booking['room_type']})")
        print(f"Check-in: {booking['check_in_date']}")
        print(f"Check-out: {booking['check_out_date']}")
        print(f"Nights: {booking['number_of_nights']}")
        print(f"Guests: {booking['number_of_guests']}")
        print(f"Status: {booking['status'].upper()}")
        print(f"Amount: ${booking['final_amount']:.2f}")
        print(f"Created by: {booking['created_by_username']}")
        
        if booking.get('checked_in_at'):
            print(f"Checked In At: {booking['checked_in_at']}")
        if booking.get('checked_out_at'):
            print(f"Checked Out At: {booking['checked_out_at']}")
        
        print("=" * 80)
        
        return booking
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Booking ID {booking_id} not found!")
        else:
            print(f"❌ Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def update_booking_status(token, booking_id, new_status):
    """Update booking status."""
    print(f"\n🔄 Updating booking {booking_id} to {new_status}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"status": new_status}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/bookings/{booking_id}/status",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        booking = response.json()
        
        print(f"\n✅ Status updated successfully!")
        print(f"   New Status: {booking['status'].upper()}")
        
        return booking
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Status update failed!")
        try:
            error = e.response.json()
            print(f"Error: {json.dumps(error, indent=2)}")
        except:
            print(f"Error: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def cancel_booking(token, booking_id):
    """Cancel a booking."""
    print(f"\n❌ Cancelling booking {booking_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings/{booking_id}/cancel",
            headers=headers
        )
        response.raise_for_status()
        booking = response.json()
        
        print(f"\n✅ Booking cancelled successfully!")
        print(f"   Booking Reference: {booking['booking_reference']}")
        print(f"   Status: {booking['status'].upper()}")
        
        return booking
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Cancellation failed!")
        try:
            error = e.response.json()
            print(f"Error: {json.dumps(error, indent=2)}")
        except:
            print(f"Error: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def get_todays_checkins(token):
    """Get today's check-ins."""
    print("\n📅 Fetching today's check-ins...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/today/checkins", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✅ Found {data['total']} check-in(s) scheduled for today")
        
        if data["bookings"]:
            for booking in data["bookings"]:
                print(f"  - Booking {booking['booking_reference']}: "
                      f"Room {booking['room_id']}, Customer {booking['customer_id']}, "
                      f"Status: {booking['status']}")
        else:
            print("No check-ins scheduled for today")
        
        return data["bookings"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch check-ins: {e}")
        return []


def get_todays_checkouts(token):
    """Get today's check-outs."""
    print("\n📅 Fetching today's check-outs...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/today/checkouts", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✅ Found {data['total']} check-out(s) scheduled for today")
        
        if data["bookings"]:
            for booking in data["bookings"]:
                print(f"  - Booking {booking['booking_reference']}: "
                      f"Room {booking['room_id']}, Customer {booking['customer_id']}, "
                      f"Status: {booking['status']}")
        else:
            print("No check-outs scheduled for today")
        
        return data["bookings"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch check-outs: {e}")
        return []


def test_status_workflow(token, booking_id):
    """Test complete booking status workflow."""
    print("\n" + "=" * 80)
    print("🧪 TEST: Complete Booking Status Workflow")
    print("=" * 80)
    
    # Get initial booking state
    print("\n1️⃣  Getting initial booking state...")
    booking = get_booking_details(token, booking_id)
    if not booking:
        print("❌ Cannot proceed with test")
        return
    
    print(f"\nInitial Status: {booking['status']}")
    
    # Step 1: Confirm booking
    input("\n▶️  Press Enter to CONFIRM booking...")
    booking = update_booking_status(token, booking_id, "confirmed")
    if booking:
        print(f"✅ Booking confirmed")
    
    # Step 2: Check-in
    input("\n▶️  Press Enter to CHECK-IN...")
    booking = update_booking_status(token, booking_id, "checked_in")
    if booking:
        print(f"✅ Customer checked in")
        get_booking_details(token, booking_id)
    
    # Step 3: Check-out
    input("\n▶️  Press Enter to CHECK-OUT...")
    booking = update_booking_status(token, booking_id, "checked_out")
    if booking:
        print(f"✅ Customer checked out")
        get_booking_details(token, booking_id)
    
    print("\n" + "=" * 80)
    print("✅ WORKFLOW TEST COMPLETED!")
    print("=" * 80)


def test_cancellation_workflow(token, booking_id):
    """Test booking cancellation."""
    print("\n" + "=" * 80)
    print("🧪 TEST: Booking Cancellation")
    print("=" * 80)
    
    # Get booking details
    print("\n1️⃣  Getting booking details...")
    booking = get_booking_details(token, booking_id)
    if not booking:
        print("❌ Cannot proceed with test")
        return
    
    print(f"\nCurrent Status: {booking['status']}")
    
    # Confirm cancellation
    confirm = input("\n⚠️  Are you sure you want to cancel this booking? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        # Cancel booking
        booking = cancel_booking(token, booking_id)
        if booking:
            print("\n✅ Cancellation successful!")
            get_booking_details(token, booking_id)
    else:
        print("❌ Cancellation aborted")
    
    print("\n" + "=" * 80)
    print("✅ CANCELLATION TEST COMPLETED!")
    print("=" * 80)


def interactive_status_update(token):
    """Interactive status update."""
    print("\n" + "=" * 80)
    print("🎯 INTERACTIVE STATUS UPDATE")
    print("=" * 80)
    
    # List pending bookings
    print("\n📋 Pending/Confirmed Bookings:")
    bookings = list_all_bookings(token)
    
    if not bookings:
        print("❌ No bookings available")
        return
    
    try:
        booking_id = int(input("\nEnter Booking ID to update: "))
        
        # Get booking details
        booking = get_booking_details(token, booking_id)
        if not booking:
            return
        
        # Show status options
        print("\n" + "=" * 80)
        print("STATUS OPTIONS")
        print("=" * 80)
        print("1. Confirm booking (pending → confirmed)")
        print("2. Check-in (confirmed → checked_in)")
        print("3. Check-out (checked_in → checked_out)")
        print("4. Cancel booking")
        print("0. Back")
        print("=" * 80)
        
        choice = input("\nEnter your choice (0-4): ").strip()
        
        if choice == "1":
            update_booking_status(token, booking_id, "confirmed")
        elif choice == "2":
            update_booking_status(token, booking_id, "checked_in")
        elif choice == "3":
            update_booking_status(token, booking_id, "checked_out")
        elif choice == "4":
            cancel_booking(token, booking_id)
        elif choice == "0":
            return
        else:
            print("❌ Invalid choice")
        
        # Show updated booking
        get_booking_details(token, booking_id)
    
    except ValueError:
        print("❌ Invalid input")


def run_all_tests(token):
    """Run all status management tests."""
    print("\n" + "=" * 80)
    print("🧪 RUNNING STATUS MANAGEMENT TESTS")
    print("=" * 80)
    
    # Get a pending booking
    bookings = list_all_bookings(token, status="pending")
    
    if not bookings:
        print("❌ No pending bookings available for testing")
        print("Create a booking first using test_bookings.py")
        return
    
    booking_id = bookings[0]['id']
    print(f"\n📌 Using Booking ID: {booking_id}")
    
    # Test status workflow
    input("\n▶️  Press Enter to run Complete Status Workflow Test...")
    test_status_workflow(token, booking_id)
    
    # Test cancellation (create new booking first)
    bookings = list_all_bookings(token, status="pending")
    if bookings:
        booking_id = bookings[0]['id']
        input("\n▶️  Press Enter to run Cancellation Test...")
        test_cancellation_workflow(token, booking_id)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)


def main():
    """Main function."""
    print("=" * 80)
    print("🏨 HOTEL MANAGEMENT SYSTEM - BOOKING STATUS MANAGEMENT")
    print("=" * 80)
    
    # Login
    token = login()
    if not token:
        return
    
    # Menu
    while True:
        print("\n" + "=" * 80)
        print("📋 MAIN MENU")
        print("=" * 80)
        print("1. List all bookings")
        print("2. List bookings by status")
        print("3. View booking details")
        print("4. Update booking status (interactive)")
        print("5. Cancel booking")
        print("6. View today's check-ins")
        print("7. View today's check-outs")
        print("8. Run all automated tests")
        print("0. Exit")
        print("=" * 80)
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == "1":
            list_all_bookings(token)
        
        elif choice == "2":
            print("\nStatus options: pending, confirmed, checked_in, checked_out, cancelled")
            status = input("Enter status: ").strip()
            list_all_bookings(token, status)
        
        elif choice == "3":
            try:
                booking_id = int(input("Enter booking ID: "))
                get_booking_details(token, booking_id)
            except ValueError:
                print("❌ Invalid ID")
        
        elif choice == "4":
            interactive_status_update(token)
        
        elif choice == "5":
            try:
                booking_id = int(input("Enter booking ID to cancel: "))
                cancel_booking(token, booking_id)
            except ValueError:
                print("❌ Invalid ID")
        
        elif choice == "6":
            get_todays_checkins(token)
        
        elif choice == "7":
            get_todays_checkouts(token)
        
        elif choice == "8":
            run_all_tests(token)
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ 'requests' module not found. Install it with:")
        print("  pip install requests")
        exit(1)
    
    main()