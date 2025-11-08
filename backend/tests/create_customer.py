#!/usr/bin/env python3
"""
Hotel Management System - Customer Creation with Optional File Upload
Test script for FastAPI backend.
"""

import requests
import json
import os

# =========================
# CONFIGURATION
# =========================
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin@123"

# Path to ID proof file (JPG, PNG, or PDF)
ID_PROOF_PATH = r"C:\Users\Msi\Pictures\Screenshots\temp.png"


def main():
    print("🏨 Hotel Management System - Customer Creation Test")
    print("=" * 60)

    # Step 1: Login and get token
    print("\n📝 Step 1: Logging in...")

    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        print(f"✅ Login successful! Token obtained: {token[:25]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
        return

    # Step 2: Create a new customer
    create_customer_with_file(token)


def create_customer_with_file(token: str):
    """
    Creates a new customer with an optional ID proof file upload.
    """
    print("\n📎 Step 2: Creating customer with file upload...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Customer details
    customer_data = {
        "first_name": "harsh",
        "last_name": "dave",
        "email": "harshdave@gmail.com",
        "phone": "9825474125",
        "address": "Adajan",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "zip_code": "395003",
        "id_type": "adhaar",
        "id_number": "P9821456321",
        "date_of_birth": "2004-11-15"
    }

    files = {}
    if os.path.exists(ID_PROOF_PATH):
        files["id_proof"] = open(ID_PROOF_PATH, "rb")
        print(f"📄 Attaching ID proof file: {os.path.basename(ID_PROOF_PATH)}")
    else:
        print("⚠️ No ID proof file found — continuing without file upload.")

    try:
        response = requests.post(
            f"{BASE_URL}/customers/",
            headers=headers,
            data=customer_data,
            files=files if files else None
        )
        response.raise_for_status()
        customer = response.json()

        print("\n✅ Customer created successfully!")
        print(json.dumps(customer, indent=2))

        if customer.get("id_proof_path"):
            print(f"📂 File saved at: {customer['id_proof_path']}")
        else:
            print("⚠️ File path not returned (may not have been uploaded).")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print("Response:", e.response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    finally:
        # Close file handle if opened
        if "id_proof" in files:
            files["id_proof"].close()

    # Step 3: Verify customer creation
    verify_customers(token)


def verify_customers(token: str):
    """
    Verifies that the customer was added successfully by listing all customers.
    """
    print("\n📋 Step 3: Verifying - Getting all customers...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(f"{BASE_URL}/customers/?skip=0&limit=10", headers=headers)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Total customers in database: {data['total']}")

        if data["customers"]:
            print("\n🧾 Recent customers:")
            for c in data["customers"][-3:]:  # Show last 3
                print(f"  - {c['first_name']} {c['last_name']} ({c['email']})")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Could not fetch customers: {e}")


# =========================
# RUN SCRIPT
# =========================
if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ 'requests' module not found. Please install it:")
        print("  pip install requests")
        exit(1)

    main()
