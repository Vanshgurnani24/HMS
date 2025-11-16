"""
Main FastAPI Application
Entry point for the Hotel Management System API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import engine, Base
from routers import auth, rooms, customers, bookings, billing
from models import User, Room, Customer, Booking, Payment

# ------------------------------
# Scheduler Imports
# ------------------------------
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sys
import os

# Add scheduler module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scheduler import update_room_status_for_today, get_upcoming_checkin_alerts


# ------------------------------
# Database Initialization
# ------------------------------
Base.metadata.create_all(bind=engine)


# ------------------------------
# FastAPI Initialization
# ------------------------------
app = FastAPI(
    title="Hotel Management System API",
    description="Backend API for Hotel Management System",
    version="1.0.0"
)


# ------------------------------
# CORS Configuration
# ------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------
# Routers
# ------------------------------
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(customers.router)
app.include_router(bookings.router)
app.include_router(billing.router)


# ------------------------------
# Scheduler Setup
# ------------------------------
scheduler = BackgroundScheduler()

def daily_tasks():
    """Run daily automated tasks"""
    print(f"\n🕐 Running daily tasks at {datetime.now()}")
    update_room_status_for_today()
    get_upcoming_checkin_alerts()

# Run daily tasks at 6:00 AM
scheduler.add_job(daily_tasks, "cron", hour=6, minute=0)
scheduler.start()


@app.on_event("startup")
async def startup_event():
    print("✅ Scheduler started - Daily tasks will run at 6:00 AM")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("⏹️  Scheduler stopped")


# ------------------------------
# Health Check Endpoints
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Hotel Management System API is running"}

@app.get("/ping")
async def ping():
    return {"status": "success", "message": "pong"}


# ------------------------------
# Run Application
# ------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
