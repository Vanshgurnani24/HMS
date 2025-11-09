#!/usr/bin/env python3
"""
Hotel Management System - Payment & Billing Test Script
Tests payment creation, invoice generation, and billing operations.
"""

import requests
import json
from datetime import datetime

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


def get_bookings(token, status=None):
    """Get list of bookings."""
    print("\n📋 Fetching bookings...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if status:
        params["status"] = status
    
    try:
        response = requests.get(f"{BASE_URL}/bookings/", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["bookings"]:
            print(f"\n✅ Found {data['total']} booking(s)")
            print("\n" + "=" * 120)
            print(f"{'ID':<5} {'Reference':<20} {'Customer':<8} {'Status':<12} {'Amount':<12} {'Has Payment?':<15}")
            print("=" * 120)
            
            for booking in data["bookings"]:
                # Check if booking has payment
                has_payment = check_booking_has_payment(token, booking['id'])
                print(f"{booking['id']:<5} {booking['booking_reference']:<20} "
                      f"{booking['customer_id']:<8} {booking['status']:<12} "
                      f"${booking['final_amount']:<11.2f} {'Yes' if has_payment else 'No':<15}")
            print("=" * 120)
        else:
            print("⚠️  No bookings found")
        
        return data["bookings"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch bookings: {e}")
        return []


def check_booking_has_payment(token, booking_id):
    """Check if booking already has payment."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{BASE_URL}/billing/payments/booking/{booking_id}/history",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            return data["total"] > 0
    except:
        pass
    return False


def create_payment(token, booking_id, payment_method, reference_number=None):
    """Create a payment for a booking."""
    print(f"\n💳 Creating payment for booking ID {booking_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, get booking details to get the amount
    booking_response = requests.get(f"{BASE_URL}/bookings/{booking_id}", headers=headers)
    if booking_response.status_code != 200:
        print(f"❌ Could not fetch booking details")
        return None
    
    booking = booking_response.json()
    amount = booking["final_amount"]
    
    payment_data = {
        "booking_id": booking_id,
        "amount": amount,
        "payment_method": payment_method,
        "reference_number": reference_number,
        "notes": f"Payment for booking {booking['booking_reference']}"
    }
    
    print(f"   Amount: ${amount:.2f}")
    print(f"   Method: {payment_method}")
    if reference_number:
        print(f"   Reference: {reference_number}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/billing/payments",
            headers=headers,
            json=payment_data
        )
        response.raise_for_status()
        payment = response.json()
        
        print("\n✅ Payment created successfully!")
        print("\n" + "=" * 80)
        print("PAYMENT DETAILS")
        print("=" * 80)
        print(f"Payment ID: {payment['id']}")
        print(f"Transaction ID: {payment['transaction_id']}")
        print(f"Invoice Number: {payment['invoice_no']}")
        print(f"Booking ID: {payment['booking_id']}")
        print(f"Amount: ${payment['amount']:.2f}")
        print(f"Payment Method: {payment['payment_method']}")
        print(f"Status: {payment['payment_status'].upper()}")
        print(f"Created: {payment['created_at']}")
        if payment.get('reference_number'):
            print(f"Reference: {payment['reference_number']}")
        print("=" * 80)
        
        return payment
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Payment creation failed!")
        print(f"Status Code: {e.response.status_code}")
        try:
            error = e.response.json()
            print(f"Error: {json.dumps(error, indent=2)}")
        except:
            print(f"Error: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def get_all_payments(token, status=None):
    """Get list of all payments."""
    print("\n💰 Fetching payments...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if status:
        params["payment_status"] = status
    
    try:
        response = requests.get(f"{BASE_URL}/billing/payments", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["payments"]:
            print(f"\n✅ Found {data['total']} payment(s)")
            print("\n" + "=" * 120)
            print(f"{'ID':<5} {'Transaction ID':<25} {'Booking':<8} {'Amount':<12} {'Method':<15} {'Status':<12}")
            print("=" * 120)
            
            for payment in data["payments"]:
                print(f"{payment['id']:<5} {payment['transaction_id']:<25} "
                      f"{payment['booking_id']:<8} ${payment['amount']:<11.2f} "
                      f"{payment['payment_method']:<15} {payment['payment_status']:<12}")
            print("=" * 120)
        else:
            print("⚠️  No payments found")
        
        return data["payments"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch payments: {e}")
        return []


def get_payment_details(token, payment_id):
    """Get detailed payment information."""
    print(f"\n🔍 Fetching payment ID {payment_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/billing/payments/{payment_id}", headers=headers)
        response.raise_for_status()
        payment = response.json()
        
        print("\n✅ Payment found!")
        print("\n" + "=" * 80)
        print("PAYMENT DETAILS")
        print("=" * 80)
        print(f"Payment ID: {payment['id']}")
        print(f"Transaction ID: {payment['transaction_id']}")
        print(f"Invoice Number: {payment['invoice_no']}")
        print(f"Booking ID: {payment['booking_id']}")
        print(f"Amount: ${payment['amount']:.2f}")
        print(f"Payment Method: {payment['payment_method']}")
        print(f"Payment Status: {payment['payment_status'].upper()}")
        print(f"Created: {payment['created_at']}")
        print(f"Updated: {payment['updated_at']}")
        if payment.get('payment_date'):
            print(f"Payment Date: {payment['payment_date']}")
        if payment.get('reference_number'):
            print(f"Reference Number: {payment['reference_number']}")
        if payment.get('notes'):
            print(f"Notes: {payment['notes']}")
        print("=" * 80)
        
        return payment
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch payment: {e}")
        return None


def update_payment_status(token, payment_id, new_status):
    """Update payment status."""
    print(f"\n🔄 Updating payment {payment_id} to {new_status}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"payment_status": new_status}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/billing/payments/{payment_id}/status",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        payment = response.json()
        
        print(f"\n✅ Status updated successfully!")
        print(f"   New Status: {payment['payment_status'].upper()}")
        if payment.get('payment_date'):
            print(f"   Payment Date: {payment['payment_date']}")
        
        return payment
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


def get_invoice(token, booking_id):
    """Generate and fetch invoice for a booking."""
    print(f"\n🧾 Generating invoice for booking ID {booking_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/billing/invoices/booking/{booking_id}",
            headers=headers
        )
        response.raise_for_status()
        invoice = response.json()
        
        print("\n✅ Invoice generated successfully!")
        print("\n" + "=" * 80)
        print("INVOICE")
        print("=" * 80)
        print(f"Invoice Number: {invoice['invoice_no']}")
        print(f"Invoice Date: {invoice['invoice_date']}")
        print(f"Booking Reference: {invoice['booking_reference']}")
        
        print("\n" + "-" * 80)
        print("CUSTOMER INFORMATION")
        print("-" * 80)
        print(f"Name: {invoice['customer_name']}")
        print(f"Email: {invoice['customer_email']}")
        print(f"Phone: {invoice['customer_phone']}")
        if invoice.get('customer_address'):
            print(f"Address: {invoice['customer_address']}")
        
        print("\n" + "-" * 80)
        print("BOOKING DETAILS")
        print("-" * 80)
        print(f"Room: {invoice['room_number']} ({invoice['room_type']})")
        print(f"Check-in: {invoice['check_in_date']}")
        print(f"Check-out: {invoice['check_out_date']}")
        print(f"Nights: {invoice['number_of_nights']}")
        
        print("\n" + "-" * 80)
        print("CHARGES")
        print("-" * 80)
        for item in invoice['items']:
            print(f"{item['description']}")
            print(f"  Quantity: {item['quantity']} x ${item['unit_price']:.2f} = ${item['amount']:.2f}")
        
        print("\n" + "-" * 80)
        print("AMOUNT BREAKDOWN")
        print("-" * 80)
        print(f"Subtotal: ${invoice['subtotal']:.2f}")
        print(f"Discount: -${invoice['discount']:.2f}")
        print(f"Tax: ${invoice['tax']:.2f}")
        print(f"\nTotal Amount: ${invoice['total_amount']:.2f}")
        
        print("\n" + "-" * 80)
        print("PAYMENT INFORMATION")
        print("-" * 80)
        print(f"Payment Status: {invoice['payment_status'].upper()}")
        if invoice.get('payment_method'):
            print(f"Payment Method: {invoice['payment_method']}")
        if invoice.get('payment_date'):
            print(f"Payment Date: {invoice['payment_date']}")
        if invoice.get('transaction_id'):
            print(f"Transaction ID: {invoice['transaction_id']}")
        
        if invoice.get('special_requests'):
            print("\n" + "-" * 80)
            print(f"Special Requests: {invoice['special_requests']}")
        
        print("=" * 80)
        
        return invoice
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to generate invoice: {e}")
        return None


def get_payment_summary(token):
    """Get payment summary statistics."""
    print("\n📊 Fetching payment summary...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/billing/summary", headers=headers)
        response.raise_for_status()
        summary = response.json()
        
        print("\n✅ Payment Summary")
        print("\n" + "=" * 80)
        print("PAYMENT STATISTICS")
        print("=" * 80)
        print(f"Total Payments: {summary['total_payments']}")
        print(f"Total Amount: ${summary['total_amount']:.2f}")
        
        print("\n" + "-" * 80)
        print("BY STATUS")
        print("-" * 80)
        print(f"Completed: {summary['completed_payments']} payments (${summary['completed_amount']:.2f})")
        print(f"Pending: {summary['pending_payments']} payments (${summary['pending_amount']:.2f})")
        print(f"Failed: {summary['failed_payments']} payments (${summary['failed_amount']:.2f})")
        
        print("\n" + "-" * 80)
        print("BY PAYMENT METHOD")
        print("-" * 80)
        for method, count in summary['payment_methods'].items():
            print(f"{method.replace('_', ' ').title()}: {count} payments")
        print("=" * 80)
        
        return summary
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch summary: {e}")
        return None


def interactive_payment_creation(token):
    """Interactive payment creation."""
    print("\n" + "=" * 80)
    print("🎯 INTERACTIVE PAYMENT CREATION")
    print("=" * 80)
    
    # Get bookings without payments
    bookings = get_bookings(token)
    
    if not bookings:
        print("\n❌ No bookings available")
        return
    
    try:
        booking_id = int(input("\nEnter Booking ID: "))
        
        print("\nPayment Methods:")
        print("1. Cash")
        print("2. Credit Card")
        print("3. Debit Card")
        print("4. UPI")
        print("5. Net Banking")
        print("6. Wallet")
        
        method_choice = input("\nSelect payment method (1-6): ").strip()
        
        method_map = {
            "1": "cash",
            "2": "credit_card",
            "3": "debit_card",
            "4": "upi",
            "5": "net_banking",
            "6": "wallet"
        }
        
        payment_method = method_map.get(method_choice)
        if not payment_method:
            print("❌ Invalid payment method")
            return
        
        reference = input("Enter reference number (optional, press Enter to skip): ").strip() or None
        
        # Create payment
        payment = create_payment(token, booking_id, payment_method, reference)
        
        if payment:
            # Ask if user wants to mark as completed
            complete = input("\n✅ Mark payment as COMPLETED? (y/n): ").strip().lower()
            if complete == 'y':
                update_payment_status(token, payment['id'], "completed")
            
            # Ask if user wants to generate invoice
            invoice_gen = input("\n📄 Generate invoice? (y/n): ").strip().lower()
            if invoice_gen == 'y':
                get_invoice(token, booking_id)
    
    except ValueError:
        print("❌ Invalid input")
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_tests(token):
    """Run comprehensive payment tests."""
    print("\n" + "=" * 80)
    print("🧪 RUNNING COMPREHENSIVE PAYMENT TESTS")
    print("=" * 80)
    
    # Get bookings
    bookings = get_bookings(token)
    
    if not bookings:
        print("❌ No bookings available for testing")
        print("Create a booking first using test_bookings.py")
        return
    
    # Find a booking without payment
    booking_id = None
    for booking in bookings:
        if not check_booking_has_payment(token, booking['id']):
            booking_id = booking['id']
            break
    
    if not booking_id:
        booking_id = bookings[0]['id']
    
    print(f"\n📌 Using Booking ID: {booking_id}")
    
    # Test 1: Create Payment
    input("\n▶️  Press Enter to run Test 1 (Create Payment)...")
    payment = create_payment(token, booking_id, "upi", "UPI123456789")
    
    if payment:
        payment_id = payment['id']
        
        # Test 2: Get Payment Details
        input("\n▶️  Press Enter to run Test 2 (Get Payment Details)...")
        get_payment_details(token, payment_id)
        
        # Test 3: Update to Completed
        input("\n▶️  Press Enter to run Test 3 (Mark as Completed)...")
        update_payment_status(token, payment_id, "completed")
        
        # Test 4: Generate Invoice
        input("\n▶️  Press Enter to run Test 4 (Generate Invoice)...")
        get_invoice(token, booking_id)
        
        # Test 5: Payment Summary
        input("\n▶️  Press Enter to run Test 5 (Payment Summary)...")
        get_payment_summary(token)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)


def main():
    """Main function."""
    print("=" * 80)
    print("🏨 HOTEL MANAGEMENT SYSTEM - BILLING & PAYMENT TESTS")
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
        print("1. View bookings")
        print("2. View all payments")
        print("3. Create payment (interactive)")
        print("4. View payment details")
        print("5. Update payment status")
        print("6. Generate invoice")
        print("7. Payment summary")
        print("8. Run all automated tests")
        print("0. Exit")
        print("=" * 80)
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == "1":
            get_bookings(token)
        
        elif choice == "2":
            print("\nFilter by status? (pending/completed/failed/refunded, or press Enter for all)")
            status = input("Status: ").strip() or None
            get_all_payments(token, status)
        
        elif choice == "3":
            interactive_payment_creation(token)
        
        elif choice == "4":
            try:
                payment_id = int(input("Enter payment ID: "))
                get_payment_details(token, payment_id)
            except ValueError:
                print("❌ Invalid ID")
        
        elif choice == "5":
            try:
                payment_id = int(input("Enter payment ID: "))
                print("\nNew status (pending/completed/failed/refunded):")
                new_status = input("Status: ").strip()
                update_payment_status(token, payment_id, new_status)
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "6":
            try:
                booking_id = int(input("Enter booking ID: "))
                get_invoice(token, booking_id)
            except ValueError:
                print("❌ Invalid ID")
        
        elif choice == "7":
            get_payment_summary(token)
        
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