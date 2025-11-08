#!/usr/bin/env python3
"""
Hotel Management System - Customer Update Test Script
Test script for updating customer information with optional file upload.
"""

import requests
import json
import os
import sys

# =========================
# CONFIGURATION
# =========================
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin@123"

# Path to new ID proof file (JPG, PNG, or PDF) for update test
NEW_ID_PROOF_PATH = r"C:\Users\Msi\Pictures\Screenshots\temp.png"


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
        print(f"✅ Login successful! Token: {token[:25]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        sys.exit(1)


def list_customers(token):
    """List all customers and return the list."""
    print("\n📋 Fetching all customers...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/customers/?skip=0&limit=100", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        customers = data["customers"]
        total = data["total"]
        
        print(f"✅ Found {total} customer(s) in database\n")
        
        if customers:
            print("=" * 80)
            print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15}")
            print("=" * 80)
            for c in customers:
                name = f"{c['first_name']} {c['last_name']}"
                print(f"{c['id']:<5} {name:<25} {c['email']:<30} {c['phone']:<15}")
            print("=" * 80)
        else:
            print("⚠️  No customers found. Create one first!")
        
        return customers
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch customers: {e}")
        return []


def get_customer_by_id(token, customer_id):
    """Get specific customer details."""
    print(f"\n🔍 Fetching customer ID: {customer_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/customers/{customer_id}", headers=headers)
        response.raise_for_status()
        customer = response.json()
        
        print("\n✅ Current Customer Details:")
        print("=" * 60)
        print(json.dumps(customer, indent=2))
        print("=" * 60)
        
        return customer
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Customer ID {customer_id} not found!")
        else:
            print(f"❌ Error: {e}")
            print("Response:", e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def update_customer_basic(token, customer_id):
    """
    Test 1: Update basic customer information (no file upload).
    """
    print(f"\n🔧 Test 1: Updating basic info for customer ID {customer_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update data - only fields you want to change
    update_data = {
        "phone": "9876543210",  # New phone number
        "address": "New Address, Varachha Road",  # New address
        "city": "Surat",
        "zip_code": "395006"  # New zip code
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=headers,
            data=update_data
        )
        response.raise_for_status()
        customer = response.json()
        
        print("\n✅ Customer updated successfully!")
        print("=" * 60)
        print("Updated Fields:")
        print(f"  Phone: {customer['phone']}")
        print(f"  Address: {customer['address']}")
        print(f"  City: {customer['city']}")
        print(f"  Zip Code: {customer['zip_code']}")
        print("=" * 60)
        
        return customer
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Update failed: {e}")
        print("Response:", e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def update_customer_with_file(token, customer_id):
    """
    Test 2: Update customer with new ID proof file.
    """
    print(f"\n📎 Test 2: Updating customer ID {customer_id} with new ID proof...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update data
    update_data = {
        "last_name": "Dave Updated",  # Change last name
        "id_type": "passport",  # Change ID type
        "id_number": "NEW123456789"  # New ID number
    }
    
    files = {}
    if os.path.exists(NEW_ID_PROOF_PATH):
        files["id_proof"] = open(NEW_ID_PROOF_PATH, "rb")
        print(f"📄 Attaching new ID proof: {os.path.basename(NEW_ID_PROOF_PATH)}")
    else:
        print(f"⚠️  File not found: {NEW_ID_PROOF_PATH}")
        print("⚠️  Continuing without file upload...")
    
    try:
        response = requests.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=headers,
            data=update_data,
            files=files if files else None
        )
        response.raise_for_status()
        customer = response.json()
        
        print("\n✅ Customer updated with new file!")
        print("=" * 60)
        print("Updated Fields:")
        print(f"  Last Name: {customer['last_name']}")
        print(f"  ID Type: {customer['id_type']}")
        print(f"  ID Number: {customer['id_number']}")
        if customer.get("id_proof_path"):
            print(f"  ID Proof Path: {customer['id_proof_path']}")
        print("=" * 60)
        
        return customer
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Update failed: {e}")
        print("Response:", e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    finally:
        if "id_proof" in files:
            files["id_proof"].close()


def update_customer_partial(token, customer_id):
    """
    Test 3: Partial update - only update email.
    """
    print(f"\n✉️  Test 3: Partial update - changing only email for customer ID {customer_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current customer first
    current = get_customer_by_id(token, customer_id)
    if not current:
        return None
    
    # Ask for new email
    print(f"\nCurrent email: {current['email']}")
    new_email = input("Enter new email (or press Enter to skip): ").strip()
    
    if not new_email:
        print("⏭️  Skipping email update")
        return current
    
    update_data = {"email": new_email}
    
    try:
        response = requests.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=headers,
            data=update_data
        )
        response.raise_for_status()
        customer = response.json()
        
        print(f"\n✅ Email updated from {current['email']} → {customer['email']}")
        return customer
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"❌ Email already in use!")
        else:
            print(f"❌ Update failed: {e}")
        print("Response:", e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def update_customer_all_fields(token, customer_id):
    """
    Test 4: Update all possible fields at once.
    """
    print(f"\n🔄 Test 4: Complete update - all fields for customer ID {customer_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "first_name": "Harsh",
        "last_name": "Dave",
        "email": "harsh.dave.updated@gmail.com",
        "phone": "7412589632",
        "address": "123 New Street, Adajan",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "zip_code": "395009",
        "id_type": "adhaar",
        "id_number": "UPDATED123456",
        "date_of_birth": "2004-11-15"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=headers,
            data=update_data
        )
        response.raise_for_status()
        customer = response.json()
        
        print("\n✅ All fields updated successfully!")
        print("=" * 60)
        print(json.dumps(customer, indent=2))
        print("=" * 60)
        
        return customer
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Update failed: {e}")
        print("Response:", e.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def search_customer(token, query):
    """Search for customers."""
    print(f"\n🔍 Searching for: {query}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/customers/search?query={query}",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        customers = data["customers"]
        print(f"✅ Found {len(customers)} matching customer(s)")
        
        if customers:
            for c in customers:
                print(f"  - ID: {c['id']}, Name: {c['first_name']} {c['last_name']}, Email: {c['email']}")
        
        return customers
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Search failed: {e}")
        return []


def interactive_update(token):
    """Interactive mode - let user choose what to update."""
    print("\n" + "=" * 60)
    print("🎯 INTERACTIVE UPDATE MODE")
    print("=" * 60)
    
    # List customers first
    customers = list_customers(token)
    
    if not customers:
        print("\n❌ No customers available. Create one first!")
        return
    
    # Get customer ID
    while True:
        try:
            customer_id = int(input("\nEnter customer ID to update (or 0 to exit): "))
            if customer_id == 0:
                print("👋 Exiting...")
                return
            break
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get customer details
    customer = get_customer_by_id(token, customer_id)
    if not customer:
        return
    
    # Show update menu
    print("\n" + "=" * 60)
    print("📝 What would you like to update?")
    print("=" * 60)
    print("1. Update basic info (phone, address, city)")
    print("2. Update with new ID proof file")
    print("3. Update only email")
    print("4. Update all fields")
    print("5. Custom update (choose fields)")
    print("0. Cancel")
    print("=" * 60)
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        update_customer_basic(token, customer_id)
    elif choice == "2":
        update_customer_with_file(token, customer_id)
    elif choice == "3":
        update_customer_partial(token, customer_id)
    elif choice == "4":
        update_customer_all_fields(token, customer_id)
    elif choice == "5":
        custom_update(token, customer_id, customer)
    elif choice == "0":
        print("👋 Cancelled")
    else:
        print("❌ Invalid choice")


def custom_update(token, customer_id, current_customer):
    """Let user specify which fields to update."""
    print("\n📝 Custom Update - Enter new values (press Enter to skip)")
    print("=" * 60)
    
    update_data = {}
    
    # Collect updates
    fields = [
        ("first_name", "First Name"),
        ("last_name", "Last Name"),
        ("email", "Email"),
        ("phone", "Phone"),
        ("address", "Address"),
        ("city", "City"),
        ("state", "State"),
        ("country", "Country"),
        ("zip_code", "Zip Code"),
        ("id_type", "ID Type"),
        ("id_number", "ID Number"),
        ("date_of_birth", "Date of Birth (YYYY-MM-DD)")
    ]
    
    for field, label in fields:
        current_value = current_customer.get(field, "N/A")
        new_value = input(f"{label} [{current_value}]: ").strip()
        if new_value:
            update_data[field] = new_value
    
    # Ask about file
    upload_file = input("\nUpdate ID proof file? (y/n): ").strip().lower()
    
    if not update_data and upload_file != 'y':
        print("⚠️  No changes to make")
        return
    
    # Perform update
    headers = {"Authorization": f"Bearer {token}"}
    files = {}
    
    if upload_file == 'y' and os.path.exists(NEW_ID_PROOF_PATH):
        files["id_proof"] = open(NEW_ID_PROOF_PATH, "rb")
        print(f"📄 Attaching: {os.path.basename(NEW_ID_PROOF_PATH)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=headers,
            data=update_data,
            files=files if files else None
        )
        response.raise_for_status()
        customer = response.json()
        
        print("\n✅ Customer updated successfully!")
        print("=" * 60)
        print(json.dumps(customer, indent=2))
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Update failed: {e}")
        print("Response:", e.response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    finally:
        if "id_proof" in files:
            files["id_proof"].close()


def run_all_tests(token):
    """Run all automated update tests."""
    print("\n" + "=" * 60)
    print("🧪 RUNNING ALL UPDATE TESTS")
    print("=" * 60)
    
    # Get first customer
    customers = list_customers(token)
    if not customers:
        print("\n❌ No customers available. Create one first!")
        return
    
    customer_id = customers[0]["id"]
    print(f"\n📌 Using customer ID: {customer_id}")
    
    # Run tests
    input("\n▶️  Press Enter to run Test 1 (Basic Info Update)...")
    update_customer_basic(token, customer_id)
    
    input("\n▶️  Press Enter to run Test 2 (Update with File)...")
    update_customer_with_file(token, customer_id)
    
    input("\n▶️  Press Enter to run Test 3 (Partial Update)...")
    update_customer_partial(token, customer_id)
    
    input("\n▶️  Press Enter to run Test 4 (Complete Update)...")
    update_customer_all_fields(token, customer_id)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)


def main():
    """Main function."""
    print("=" * 60)
    print("🏨 HOTEL MANAGEMENT SYSTEM - CUSTOMER UPDATE TESTS")
    print("=" * 60)
    
    # Login
    token = login()
    
    # Show menu
    while True:
        print("\n" + "=" * 60)
        print("📋 MAIN MENU")
        print("=" * 60)
        print("1. List all customers")
        print("2. View specific customer")
        print("3. Interactive update")
        print("4. Run all automated tests")
        print("5. Search customers")
        print("0. Exit")
        print("=" * 60)
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            list_customers(token)
        
        elif choice == "2":
            try:
                customer_id = int(input("Enter customer ID: "))
                get_customer_by_id(token, customer_id)
            except ValueError:
                print("❌ Invalid ID")
        
        elif choice == "3":
            interactive_update(token)
        
        elif choice == "4":
            run_all_tests(token)
        
        elif choice == "5":
            query = input("Enter search query (name/email/phone): ").strip()
            if query:
                search_customer(token, query)
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


# =========================
# RUN SCRIPT
# =========================
if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ 'requests' module not found. Please install it:")
        print("  pip install requests")
        sys.exit(1)
    
    main()