"""
Main FastAPI Application
Entry point for the Hotel Management System API.

UPDATED Day 7: Added reports router for analytics and reporting module.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import engine, Base
from routers import auth, rooms, customers, reports  # <-- UPDATED: Added reports import
from models import User, Room, Customer, Booking, Payment

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Management System API",
    description="Backend API for Hotel Management System - Now with Reports & Analytics",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(customers.router)
app.include_router(reports.router)  # <-- UPDATED: Added reports router for Day 7

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Hotel Management System API is running",
        "version": "1.0.0",
        "modules": ["auth", "rooms", "customers", "bookings", "payments", "reports"]
    }

# Ping endpoint for testing
@app.get("/ping")
async def ping():
    return {"status": "success", "message": "pong"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)