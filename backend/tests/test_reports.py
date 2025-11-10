#!/usr/bin/env python3
"""
Hotel Management System - Day 7 Reports Module Testing
Comprehensive test script for all reporting and analytics endpoints.

Tests:
1. Occupancy Report - Overall
2. Occupancy Report - By Room Type
3. Daily Revenue Report
4. Revenue Report - Date Range
5. Booking History Report
6. Upcoming Bookings Report
7. Dashboard Summary
8. Top Customers Report
"""

import requests
import json
from datetime import date, timedelta
from typing import Dict, Any

# =========================
# CONFIGURATION
# =========================
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin@123"


class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{title.center(80)}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.END}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Color.GREEN}✅ {message}{Color.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Color.RED}❌ {message}{Color.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Color.BLUE}ℹ️  {message}{Color.END}")


def print_json(data: Dict[Any, Any], title: str = "Response"):
    """Print formatted JSON"""
    print(f"\n{Color.YELLOW}{title}:{Color.END}")
    print(json.dumps(data, indent=2, default=str))


def login() -> str:
    """Login and return JWT token"""
    print_info("Logging in...")
    
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print_success(f"Login successful! Token: {token[:30]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print_error(f"Login failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        raise


def test_occupancy_report(token: str):
    """Test 1: Overall Occupancy Report"""
    print_section("TEST 1: Overall Occupancy Report")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/reports/occupancy", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print_success("Occupancy report retrieved successfully!")
        print_json(data)
        
        # Print summary
        print(f"\n{Color.BOLD}Summary:{Color.END}")
        print(f"  Total Rooms: {data['total_rooms']}")
        print(f"  Active Rooms: {data['active_rooms']}")
        print(f"  Overall Occupancy Rate: {data['overall_occupancy_rate']}%")
        print(f"  Available for Booking: {data['available_for_booking']}")
        
        print(f"\n{Color.BOLD}By Status:{Color.END}")
        for status in data['by_status']:
            print(f"  {status['status']}: {status['count']}")
        
        print(f"\n{Color.BOLD}By Room Type:{Color.END}")
        for room_type in data['by_type']:
            print(f"  {room_type['room_type']}:")
            print(f"    Total: {room_type['total_rooms']}, Occupancy: {room_type['occupancy_rate']}%")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_occupancy_by_type(token: str):
    """Test 2: Occupancy Report by Room Type"""
    print_section("TEST 2: Occupancy Report by Room Type")
    
    headers = {"Authorization": f"Bearer {token}"}
    room_types = ["single", "double", "suite", "deluxe"]
    
    for room_type in room_types:
        print(f"\n{Color.BOLD}Testing {room_type.upper()}:{Color.END}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/reports/occupancy/type/{room_type}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            print_success(f"{room_type} occupancy retrieved!")
            print(f"  Total: {data['total_rooms']}")
            print(f"  Available: {data['available']}")
            print(f"  Occupied: {data['occupied']}")
            print(f"  Reserved: {data['reserved']}")
            print(f"  Maintenance: {data['maintenance']}")
            print(f"  Occupancy Rate: {data['occupancy_rate']}%")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print_info(f"No rooms found for type: {room_type}")
            else:
                print_error(f"Error: {e}")
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")


def test_daily_revenue(token: str):
    """Test 3: Daily Revenue Report"""
    print_section("TEST 3: Daily Revenue Report")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test for today
    today = date.today()
    
    print(f"{Color.BOLD}Testing for date: {today}{Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/revenue/daily",
            headers=headers,
            params={"target_date": str(today)}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Daily revenue report retrieved!")
        print_json(data)
        
        print(f"\n{Color.BOLD}Summary:{Color.END}")
        print(f"  Date: {data['date']}")
        print(f"  Total Revenue: ₹{data['total_revenue']:.2f}")
        print(f"  Completed Payments: {data['completed_payments']}")
        print(f"  Pending Payments: {data['pending_payments']}")
        print(f"  Failed Payments: {data['failed_payments']}")
        print(f"  Refunded Amount: ₹{data['refunded_amount']:.2f}")
        print(f"  Net Revenue: ₹{data['net_revenue']:.2f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_revenue_range(token: str):
    """Test 4: Revenue Report for Date Range"""
    print_section("TEST 4: Revenue Report - Date Range")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test for last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    print(f"{Color.BOLD}Testing date range: {start_date} to {end_date}{Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/revenue/range",
            headers=headers,
            params={
                "start_date": str(start_date),
                "end_date": str(end_date)
            }
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Revenue range report retrieved!")
        print_json(data)
        
        print(f"\n{Color.BOLD}Summary:{Color.END}")
        print(f"  Period: {data['start_date']} to {data['end_date']}")
        print(f"  Total Revenue: ₹{data['total_revenue']:.2f}")
        print(f"  Total Bookings: {data['total_bookings']}")
        print(f"  Average Booking Value: ₹{data['average_booking_value']:.2f}")
        
        if data['by_payment_method']:
            print(f"\n{Color.BOLD}By Payment Method:{Color.END}")
            for method in data['by_payment_method']:
                print(f"  {method['payment_method']}: ₹{method['total_amount']:.2f} ({method['transaction_count']} transactions)")
        
        print(f"\n{Color.BOLD}Daily Breakdown:{Color.END}")
        for day in data['daily_breakdown']:
            print(f"  {day['date']}: ₹{day['revenue']:.2f} ({day['booking_count']} bookings)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_booking_history(token: str):
    """Test 5: Booking History Report"""
    print_section("TEST 5: Booking History Report")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with date range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"{Color.BOLD}Testing last 30 days: {start_date} to {end_date}{Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/bookings/history",
            headers=headers,
            params={
                "start_date": str(start_date),
                "end_date": str(end_date),
                "limit": 10
            }
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Booking history retrieved!")
        
        print(f"\n{Color.BOLD}Summary:{Color.END}")
        print(f"  Total Bookings: {data['total_bookings']}")
        print(f"  Showing: {len(data['bookings'])} bookings")
        
        print(f"\n{Color.BOLD}Status Breakdown:{Color.END}")
        for status, count in data['status_breakdown'].items():
            print(f"  {status}: {count}")
        
        if data['bookings']:
            print(f"\n{Color.BOLD}Recent Bookings:{Color.END}")
            for booking in data['bookings'][:5]:  # Show first 5
                print(f"  [{booking['booking_reference']}] {booking['customer_name']} - "
                      f"Room {booking['room_number']} ({booking['room_type']}) - "
                      f"{booking['status']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_upcoming_bookings(token: str):
    """Test 6: Upcoming Bookings Report"""
    print_section("TEST 6: Upcoming Bookings Report")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"{Color.BOLD}Testing upcoming bookings (next 7 days){Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/bookings/upcoming",
            headers=headers,
            params={"days": 7}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Upcoming bookings retrieved!")
        
        print(f"\n{Color.BOLD}Summary:{Color.END}")
        print(f"  Total Upcoming: {data['total_bookings']}")
        print(f"  Period: {data['start_date']} to {data['end_date']}")
        
        if data['bookings']:
            print(f"\n{Color.BOLD}Upcoming Check-ins:{Color.END}")
            for booking in data['bookings']:
                print(f"  {booking['check_in_date']}: [{booking['booking_reference']}] "
                      f"{booking['customer_name']} - Room {booking['room_number']}")
        else:
            print_info("No upcoming bookings in the next 7 days")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_dashboard_summary(token: str):
    """Test 7: Dashboard Summary"""
    print_section("TEST 7: Dashboard Summary")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/reports/dashboard", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print_success("Dashboard summary retrieved!")
        
        stats = data['quick_stats']
        
        print(f"\n{Color.BOLD}Quick Statistics:{Color.END}")
        print(f"  Total Rooms: {stats['total_rooms']}")
        print(f"  Occupied: {stats['occupied_rooms']}")
        print(f"  Available: {stats['available_rooms']}")
        print(f"  Total Customers: {stats['total_customers']}")
        print(f"  Active Bookings: {stats['active_bookings']}")
        print(f"  Today's Check-ins: {stats['todays_checkins']}")
        print(f"  Today's Check-outs: {stats['todays_checkouts']}")
        print(f"  Today's Revenue: ₹{stats['todays_revenue']:.2f}")
        print(f"  Pending Payments: {stats['pending_payments']} (₹{stats['pending_payment_amount']:.2f})")
        
        print(f"\n{Color.BOLD}Overall Occupancy Rate: {data['occupancy_rate']}%{Color.END}")
        
        print(f"\n{Color.BOLD}Recent Bookings (Last {len(data['recent_bookings'])}):{Color.END}")
        for booking in data['recent_bookings'][:5]:
            print(f"  [{booking['booking_reference']}] {booking['customer_name']} - "
                  f"Room {booking['room_number']} ({booking['status']})")
        
        print(f"\n{Color.BOLD}Revenue Trend (Last 7 Days):{Color.END}")
        for day in data['revenue_trend']:
            print(f"  {day['date']}: ₹{day['revenue']:.2f} ({day['booking_count']} bookings)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def test_top_customers(token: str):
    """Test 8: Top Customers Report"""
    print_section("TEST 8: Top Customers Report")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test by revenue
    print(f"\n{Color.BOLD}Top 10 Customers by Revenue:{Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/customers/top",
            headers=headers,
            params={"report_type": "by_revenue", "limit": 10}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Top customers (by revenue) retrieved!")
        
        if data['customers']:
            for i, customer in enumerate(data['customers'], 1):
                print(f"  {i}. {customer['customer_name']} ({customer['customer_email']})")
                print(f"     Total Spent: ₹{customer['total_spent']:.2f}")
                print(f"     Bookings: {customer['total_bookings']} "
                      f"(Completed: {customer['completed_bookings']}, "
                      f"Cancelled: {customer['cancelled_bookings']})")
                print(f"     Average Booking Value: ₹{customer['average_booking_value']:.2f}")
                print(f"     Last Booking: {customer['last_booking_date']}\n")
        else:
            print_info("No customer data available")
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
    
    # Test by bookings
    print(f"\n{Color.BOLD}Top 5 Customers by Booking Count:{Color.END}\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reports/customers/top",
            headers=headers,
            params={"report_type": "by_bookings", "limit": 5}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success("Top customers (by bookings) retrieved!")
        
        if data['customers']:
            for i, customer in enumerate(data['customers'], 1):
                print(f"  {i}. {customer['customer_name']} - {customer['total_bookings']} bookings")
        else:
            print_info("No customer data available")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return False


def run_all_tests():
    """Run all report tests"""
    print(f"\n{Color.BOLD}{Color.HEADER}")
    print("=" * 80)
    print("HOTEL MANAGEMENT SYSTEM - DAY 7 REPORTS MODULE TESTING".center(80))
    print("=" * 80)
    print(Color.END)
    
    # Login
    try:
        token = login()
    except Exception as e:
        print_error(f"Failed to login: {e}")
        return
    
    # Track results
    results = {
        "Test 1 - Occupancy Report": test_occupancy_report(token),
        "Test 2 - Occupancy by Type": test_occupancy_by_type(token),
        "Test 3 - Daily Revenue": test_daily_revenue(token),
        "Test 4 - Revenue Range": test_revenue_range(token),
        "Test 5 - Booking History": test_booking_history(token),
        "Test 6 - Upcoming Bookings": test_upcoming_bookings(token),
        "Test 7 - Dashboard Summary": test_dashboard_summary(token),
        "Test 8 - Top Customers": test_top_customers(token),
    }
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Color.GREEN}✅ PASSED{Color.END}" if result else f"{Color.RED}❌ FAILED{Color.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Color.BOLD}Overall Result: {passed}/{total} tests passed{Color.END}")
    
    if passed == total:
        print_success("All tests passed! 🎉")
    else:
        print_error(f"{total - passed} test(s) failed")


# =========================
# INTERACTIVE MENU
# =========================

def interactive_menu():
    """Interactive menu for selective testing"""
    while True:
        print(f"\n{Color.BOLD}{Color.CYAN}=" * 80)
        print("REPORTS MODULE - INTERACTIVE TEST MENU".center(80))
        print("=" * 80)
        print(Color.END)
        print("\n1.  Test Occupancy Report (Overall)")
        print("2.  Test Occupancy by Room Type")
        print("3.  Test Daily Revenue Report")
        print("4.  Test Revenue Range Report")
        print("5.  Test Booking History")
        print("6.  Test Upcoming Bookings")
        print("7.  Test Dashboard Summary")
        print("8.  Test Top Customers")
        print("9.  Run All Tests")
        print("0.  Exit")
        
        choice = input(f"\n{Color.BOLD}Enter your choice (0-9): {Color.END}").strip()
        
        if choice == "0":
            print_info("Goodbye! 👋")
            break
        
        try:
            token = login()
        except Exception:
            continue
        
        if choice == "1":
            test_occupancy_report(token)
        elif choice == "2":
            test_occupancy_by_type(token)
        elif choice == "3":
            test_daily_revenue(token)
        elif choice == "4":
            test_revenue_range(token)
        elif choice == "5":
            test_booking_history(token)
        elif choice == "6":
            test_upcoming_bookings(token)
        elif choice == "7":
            test_dashboard_summary(token)
        elif choice == "8":
            test_top_customers(token)
        elif choice == "9":
            run_all_tests()
        else:
            print_error("Invalid choice!")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    import sys
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print_error("'requests' module not found. Please install it:")
        print("  pip install requests")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Run all tests automatically
        run_all_tests()
    else:
        # Interactive menu
        interactive_menu()