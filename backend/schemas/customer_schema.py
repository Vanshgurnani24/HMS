"""
Customer Pydantic schemas for request/response validation.
Handles customer data validation, creation, updates, and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


# Customer Schemas
class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    id_type: Optional[str] = Field(None, description="passport, driver_license, national_id, etc.")
    id_number: Optional[str] = None
    date_of_birth: Optional[date] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating customer details (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[date] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response (includes all fields)"""
    id: int
    id_proof_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Schema for paginated customer list response"""
    total: int
    customers: list[CustomerResponse]


class CustomerSearchResponse(BaseModel):
    """Schema for customer search results"""
    customers: list[CustomerResponse]