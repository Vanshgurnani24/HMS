#!/usr/bin/env python3
"""
Hotel Management System - Booking Creation Test Script
Tests booking creation with various scenarios including availability checks.
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
    
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        return token
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        return None


def get_available_rooms(token):
    """Get list of available rooms."""
    print("\n🏨 Fetching available rooms...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/rooms/available/check",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["rooms"]:
            print(f"✅ Found {data['total']} available room(s)")
            print("\n" + "=" * 80)
            print(f"{'ID':<5} {'Room #':<10} {'Type':<10} {'Price':<10} {'Capacity':<10}")
            print("=" * 80)
            for room in data["rooms"][:5]:  # Show first 5
                print(f"{room['id']:<5} {room['room_number']:<10} {room['room_type']:<10} ${room['price_per_night']:<9.2f} {room['capacity']:<10}")
            print("=" * 80)
            return data["rooms"]
        else:
            print("⚠️  No available rooms found")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch rooms: {e}")
        return []


def get_customers(token):
    """Get list of customers."""
    print("\n👥 Fetching customers...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/customers/?skip=0&limit=10",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data["customers"]:
            print(f"✅ Found {data['total']} customer(s)")
            print("\n" + "=" * 80)
            print(f"{'ID':<5} {'Name':<25} {'Email':<30}")
            print("=" * 80)
            for customer in data["customers"][:5]:  # Show first 5
                name = f"{customer['first_name']} {customer['last_name']}"
                print(f"{customer['id']:<5} {name:<25} {customer['email']:<30}")
            print("=" * 80)
            return data["customers"]
        else:
            print("⚠️  No customers found")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch customers: {e}")
        return []


def check_availability(token, room_id, check_in, check_out):
    """Check if a room is available for given dates."""
    print(f"\n🔍 Checking availability for room ID {room_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "room_id": room_id,
        "check_in_date": check_in,
        "check_out_date": check_out
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings/check-availability",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        if result["available"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            if result.get("conflicting_bookings"):
                print("Conflicting bookings:")
                for booking in result["conflicting_bookings"]:
                    print(f"  - {booking}")
        
        return result["available"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Availability check failed: {e}")
        return False


def create_booking(token, customer_id, room_id, check_in, check_out, guests, discount=0.0):
    """Create a new booking."""
    print(f"\n📝 Creating booking...")
    print(f"   Customer ID: {customer_id}")
    print(f"   Room ID: {room_id}")
    print(f"   Check-in: {check_in}")
    print(f"   Check-out: {check_out}")
    print(f"   Guests: {guests}")
    print(f"   Discount: ${discount}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    booking_data = {
        "customer_id": customer_id,
        "room_id": room_id,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "number_of_guests": guests,
        "discount": discount,
        "special_requests": "Early check-in if possible"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings/",
            headers=headers,
            json=booking_data
        )
        response.raise_for_status()
        booking = response.json()
        
        print("\n✅ Booking created successfully!")
        print("\n" + "=" * 80)
        print("BOOKING DETAILS")
        print("=" * 80)
        print(f"Booking Reference: {booking['booking_reference']}")
        print(f"Customer ID: {booking['customer_id']}")
        print(f"Room ID: {booking['room_id']}")
        print(f"Check-in: {booking['check_in_date']}")
        print(f"Check-out: {booking['check_out_date']}")
        print(f"Nights: {booking['number_of_nights']}")
        print(f"Guests: {booking['number_of_guests']}")
        print(f"Status: {booking['status']}")
        print("\n" + "-" * 80)
        print("COST BREAKDOWN")
        print("-" * 80)
        print(f"Room Price/Night: ${booking['room_price']:.2f}")
        print(f"Total (before discount): ${booking['total_amount']:.2f}")
        print(f"Discount: -${booking['discount']:.2f}")
        print(f"Tax (12%): ${booking['tax']:.2f}")
        print(f"Final Amount: ${booking['final_amount']:.2f}")
        print("=" * 80)
        
        return booking
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Booking creation failed!")
        print(f"Status Code: {e.response.status_code}")
        try:
            error_detail = e.response.json()
            print(f"Error: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"Error: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def get_booking_by_reference(token, booking_ref):
    """Get booking details by reference."""
    print(f"\n🔍 Fetching booking {booking_ref}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/bookings/reference/{booking_ref}",
            headers=headers
        )
        response.raise_for_status()
        booking = response.json()
        
        print("\n✅ Booking found!")
        print("\n" + "=" * 80)
        print("DETAILED BOOKING INFORMATION")
        print("=" * 80)
        print(f"Booking Reference: {booking['booking_reference']}")
        print(f"Customer: {booking['customer_name']}")
        print(f"Email: {booking['customer_email']}")
        print(f"Phone: {booking['customer_phone']}")
        print(f"Room: {booking['room_number']} ({booking['room_type']})")
        print(f"Check-in: {booking['check_in_date']}")
        print(f"Check-out: {booking['check_out_date']}")
        print(f"Nights: {booking['number_of_nights']}")
        print(f"Guests: {booking['number_of_guests']}")
        print(f"Status: {booking['status']}")
        print(f"Final Amount: ${booking['final_amount']:.2f}")
        print(f"Created by: {booking['created_by_username']}")
        print("=" * 80)
        
        return booking
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch booking: {e}")
        return None


def get_booking_receipt(token, booking_id):
    """Get booking receipt."""
    print(f"\n🧾 Generating receipt for booking ID {booking_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/bookings/{booking_id}/receipt",
            headers=headers
        )
        response.raise_for_status()
        receipt = response.json()
        
        print("\n" + "=" * 80)
        print("BOOKING RECEIPT")
        print("=" * 80)
        print(f"Booking Reference: {receipt['booking_reference']}")
        print(f"Date: {receipt['created_at']}")
        print("\n" + "-" * 80)
        print("CUSTOMER INFORMATION")
        print("-" * 80)
        print(f"Name: {receipt['customer_name']}")
        print(f"Email: {receipt['customer_email']}")
        print("\n" + "-" * 80)
        print("ROOM INFORMATION")
        print("-" * 80)
        print(f"Room Number: {receipt['room_number']}")
        print(f"Room Type: {receipt['room_type']}")
        print("\n" + "-" * 80)
        print("STAY DETAILS")
        print("-" * 80)
        print(f"Check-in Date: {receipt['check_in_date']}")
        print(f"Check-out Date: {receipt['check_out_date']}")
        print(f"Number of Nights: {receipt['number_of_nights']}")
        print(f"Number of Guests: {receipt['number_of_guests']}")
        print("\n" + "-" * 80)
        print("COST BREAKDOWN")
        print("-" * 80)
        print(f"Room Rate (per night): ${receipt['room_price_per_night']:.2f}")
        print(f"Subtotal: ${receipt['subtotal']:.2f}")
        print(f"Discount: -${receipt['discount']:.2f}")
        print(f"Tax: ${receipt['tax']:.2f}")
        print(f"\nTotal Amount: ${receipt['final_amount']:.2f}")
        print("\n" + "-" * 80)
        print(f"Booking Status: {receipt['booking_status'].upper()}")
        if receipt['special_requests']:
            print(f"Special Requests: {receipt['special_requests']}")
        print("=" * 80)
        
        return receipt
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get receipt: {e}")
        return None


def test_double_booking(token, room_id, check_in, check_out, customer_id, guests):
    """Test double-booking prevention."""
    print("\n" + "=" * 80)
    print("🧪 TEST: Double-Booking Prevention")
    print("=" * 80)
    
    print("\n1️⃣  Creating first booking...")
    booking1 = create_booking(token, customer_id, room_id, check_in, check_out, guests)
    
    if not booking1:
        print("❌ First booking failed. Cannot test double-booking.")
        return
    
    print("\n2️⃣  Attempting to create overlapping booking...")
    print("Expected: Should fail with conflict error")
    
    booking2 = create_booking(token, customer_id, room_id, check_in, check_out, guests)
    
    if booking2:
        print("❌ TEST FAILED: Double-booking was allowed!")
    else:
        print("✅ TEST PASSED: Double-booking was prevented!")


def interactive_booking(token):
    """Interactive booking creation."""
    print("\n" + "=" * 80)
    print("🎯 INTERACTIVE BOOKING CREATION")
    print("=" * 80)
    
    # Get customers
    customers = get_customers(token)
    if not customers:
        print("\n❌ No customers available. Create a customer first!")
        return
    
    # Get rooms
    rooms = get_available_rooms(token)
    if not rooms:
        print("\n❌ No available rooms. Cannot create booking!")
        return
    
    # Get inputs
    try:
        customer_id = int(input("\nEnter Customer ID: "))
        room_id = int(input("Enter Room ID: "))
        
        # Default dates (today + 1 day to today + 3 days)
        default_checkin = (date.today() + timedelta(days=1)).isoformat()
        default_checkout = (date.today() + timedelta(days=3)).isoformat()
        
        check_in = input(f"Check-in date (YYYY-MM-DD) [{default_checkin}]: ").strip() or default_checkin
        check_out = input(f"Check-out date (YYYY-MM-DD) [{default_checkout}]: ").strip() or default_checkout
        guests = int(input("Number of guests: "))
        discount = float(input("Discount amount (0 for none): ") or "0")
        
        # Check availability first
        if check_availability(token, room_id, check_in, check_out):
            # Create booking
            booking = create_booking(token, customer_id, room_id, check_in, check_out, guests, discount)
            
            if booking:
                # Fetch detailed info
                get_booking_by_reference(token, booking['booking_reference'])
                
                # Generate receipt
                get_receipt = input("\n📄 Generate receipt? (y/n): ").strip().lower()
                if get_receipt == 'y':
                    get_booking_receipt(token, booking['id'])
        else:
            print("\n⚠️  Room not available for selected dates")
    
    except ValueError:
        print("❌ Invalid input")
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_tests(token):
    """Run comprehensive booking tests."""
    print("\n" + "=" * 80)
    print("🧪 RUNNING COMPREHENSIVE BOOKING TESTS")
    print("=" * 80)
    
    # Get test data
    customers = get_customers(token)
    rooms = get_available_rooms(token)
    
    if not customers or not rooms:
        print("❌ Insufficient test data. Need at least 1 customer and 1 room.")
        return
    
    customer_id = customers[0]['id']
    room_id = rooms[0]['id']
    
    # Test dates
    check_in = (date.today() + timedelta(days=7)).isoformat()
    check_out = (date.today() + timedelta(days=10)).isoformat()
    
    print(f"\n📌 Using Customer ID: {customer_id}")
    print(f"📌 Using Room ID: {room_id}")
    print(f"📌 Check-in: {check_in}")
    print(f"📌 Check-out: {check_out}")
    
    # Test 1: Availability Check
    input("\n▶️  Press Enter to run Test 1 (Availability Check)...")
    check_availability(token, room_id, check_in, check_out)
    
    # Test 2: Create Booking
    input("\n▶️  Press Enter to run Test 2 (Create Booking)...")
    booking = create_booking(token, customer_id, room_id, check_in, check_out, 2, 50.0)
    
    if booking:
        # Test 3: Get Booking Details
        input("\n▶️  Press Enter to run Test 3 (Get Booking Details)...")
        get_booking_by_reference(token, booking['booking_reference'])
        
        # Test 4: Generate Receipt
        input("\n▶️  Press Enter to run Test 4 (Generate Receipt)...")
        get_booking_receipt(token, booking['id'])
        
        # Test 5: Double-Booking Prevention
        input("\n▶️  Press Enter to run Test 5 (Double-Booking Prevention)...")
        test_double_booking(token, room_id, check_in, check_out, customer_id, 2)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)


def main():
    """Main function."""
    print("=" * 80)
    print("🏨 HOTEL MANAGEMENT SYSTEM - BOOKING CREATION TESTS")
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
        print("1. View available rooms")
        print("2. View customers")
        print("3. Check room availability")
        print("4. Create booking (interactive)")
        print("5. Run all automated tests")
        print("0. Exit")
        print("=" * 80)
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            get_available_rooms(token)
        
        elif choice == "2":
            get_customers(token)
        
        elif choice == "3":
            try:
                room_id = int(input("Enter room ID: "))
                check_in = input("Check-in date (YYYY-MM-DD): ")
                check_out = input("Check-out date (YYYY-MM-DD): ")
                check_availability(token, room_id, check_in, check_out)
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "4":
            interactive_booking(token)
        
        elif choice == "5":
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