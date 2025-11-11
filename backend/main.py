"""
Main FastAPI Application
Entry point for the Hotel Management System API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import engine, Base
from routers import auth, rooms, customers, bookings, payments  # ← ADD bookings, payments
from models import User, Room, Customer, Booking, Payment

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Management System API",
    description="Backend API for Hotel Management System",
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
app.include_router(bookings.router)  # ← ADD THIS
app.include_router(payments.router)  # ← ADD THIS

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Hotel Management System API is running"}

# Ping endpoint for testing
@app.get("/ping")
async def ping():
    return {"status": "success", "message": "pong"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)