"""
Customer Management Router
Handles customer registration, profile management, and document upload.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import date, datetime
import os
import shutil
from pathlib import Path
import uuid

from database import get_db
from models.customer import Customer
from models.user import User, UserRole
from schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerSearchResponse
)
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/customers", tags=["Customer Management"])

# Directory for storing ID proof documents
UPLOAD_DIR = Path("uploads/id_proofs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions for ID proof
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read file to memory to get size)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )


def save_upload_file(upload_file: UploadFile, customer_id: int) -> str:
    """Save uploaded file and return the file path"""
    file_ext = Path(upload_file.filename).suffix.lower()
    file_name = f"customer_{customer_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return str(file_path)


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    id_type: Optional[str] = Form(None),
    id_number: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    id_proof: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Create a new customer profile.
    
    **Required Fields:**
    - **first_name**: Customer's first name (required)
    - **last_name**: Customer's last name (required)
    - **email**: Valid email address (required, unique)
    - **phone**: Contact number (required)
    - **address**: Street address (optional)
    - **city**: City name (optional)
    - **state**: State/Province (optional)
    - **country**: Country (optional)
    - **zip_code**: Postal code (optional)
    - **id_type**: Type of ID (passport, driver_license, national_id, etc.)
    - **id_number**: ID number (optional)
    - **date_of_birth**: Date of birth in YYYY-MM-DD format (optional)
    - **id_proof**: ID proof document (JPG, PNG, or PDF, max 5MB)
    """
    # Check if email already exists
    existing_customer = db.query(Customer).filter(Customer.email == email).first()
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with email '{email}' already exists"
        )
    
    # Validate and save ID proof if provided
    id_proof_path = None
    if id_proof:
        validate_file(id_proof)
        # We'll save the file after creating the customer to get the ID
    
    # Parse date_of_birth if provided
    parsed_dob = None
    if date_of_birth:
        try:
            parsed_dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    # Create new customer
    new_customer = Customer(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        country=country,
        zip_code=zip_code,
        id_type=id_type,
        id_number=id_number,
        date_of_birth=parsed_dob
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Save ID proof file if provided
    if id_proof:
        id_proof_path = save_upload_file(id_proof, new_customer.id)
        new_customer.id_proof_path = id_proof_path
        db.commit()
        db.refresh(new_customer)
    
    return new_customer


@router.get("/", response_model=CustomerListResponse)
def get_all_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all customers with optional filters.
    
    **Filters:**
    - **city**: Filter by city
    - **state**: Filter by state
    - **country**: Filter by country
    
    **Pagination:**
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return (max 100)
    """
    query = db.query(Customer)
    
    # Apply filters
    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Customer.state.ilike(f"%{state}%"))
    if country:
        query = query.filter(Customer.country.ilike(f"%{country}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    customers = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "customers": customers
    }


@router.get("/search", response_model=CustomerSearchResponse)
def search_customers(
    query: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search customers by name, email, or phone.
    
    - **query**: Search term (searches in first_name, last_name, full name, email, phone)
    
    This endpoint now supports:
    - First name only: "John"
    - Last name only: "Doe"
    - Full name: "John Doe"
    - Email: "john@example.com"
    - Phone: "1234567890"
    """
    search_pattern = f"%{query}%"
    
    # SQLite concatenation for full name search
    full_name = func.concat(Customer.first_name, ' ', Customer.last_name)
    
    customers = db.query(Customer).filter(
        or_(
            Customer.first_name.ilike(search_pattern),
            Customer.last_name.ilike(search_pattern),
            Customer.email.ilike(search_pattern),
            Customer.phone.ilike(search_pattern),
            full_name.ilike(search_pattern)
        )
    ).all()
    
    return {"customers": customers}


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific customer by ID.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    id_type: Optional[str] = Form(None),
    id_number: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    id_proof: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """
    Update customer details.
    
    You can update any combination of fields. New ID proof will replace the old one.
    All fields are optional - only provided fields will be updated.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Check if new email already exists (if updating email)
    if email and email != customer.email:
        existing_customer = db.query(Customer).filter(
            Customer.email == email,
            Customer.id != customer_id
        ).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{email}' is already in use"
            )
    
    # Update basic fields
    if first_name is not None:
        customer.first_name = first_name
    if last_name is not None:
        customer.last_name = last_name
    if email is not None:
        customer.email = email
    if phone is not None:
        customer.phone = phone
    if address is not None:
        customer.address = address
    if city is not None:
        customer.city = city
    if state is not None:
        customer.state = state
    if country is not None:
        customer.country = country
    if zip_code is not None:
        customer.zip_code = zip_code
    if id_type is not None:
        customer.id_type = id_type
    if id_number is not None:
        customer.id_number = id_number
    
    # Parse and update date_of_birth if provided
    if date_of_birth is not None:
        try:
            parsed_dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            customer.date_of_birth = parsed_dob
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    # Handle ID proof upload
    if id_proof:
        validate_file(id_proof)
        
        # Delete old file if it exists
        if customer.id_proof_path and os.path.exists(customer.id_proof_path):
            try:
                os.remove(customer.id_proof_path)
            except Exception:
                pass  # Continue even if deletion fails
        
        # Save new file
        id_proof_path = save_upload_file(id_proof, customer.id)
        customer.id_proof_path = id_proof_path
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete a customer (Admin only).
    
    **Warning**: This permanently deletes the customer from the database.
    Cannot delete customers with existing bookings.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Check if customer has any bookings
    if customer.bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer with existing bookings."
        )
    
    # Delete ID proof file if it exists
    if customer.id_proof_path and os.path.exists(customer.id_proof_path):
        try:
            os.remove(customer.id_proof_path)
        except Exception:
            pass  # Continue even if deletion fails
    
    db.delete(customer)
    db.commit()
    
    return None


@router.get("/email/{email}", response_model=CustomerResponse)
def get_customer_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer details by email address.
    
    Useful for checking if a customer exists before creating a booking.
    """
    customer = db.query(Customer).filter(Customer.email == email).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with email '{email}' not found"
        )
    
    return customer


@router.get("/phone/{phone}", response_model=CustomerResponse)
def get_customer_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer details by phone number.
    
    Useful for quick customer lookup during check-in.
    """
    customer = db.query(Customer).filter(Customer.phone == phone).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with phone '{phone}' not found"
        )
    
    return customer