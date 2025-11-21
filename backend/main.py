"""
Main FastAPI Application
Entry point for the Hotel Management System API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base, SessionLocal
from routers import auth, rooms, customers, bookings, billing, reports, settings, room_types
from models import User, Room, Customer, Booking, Payment, HotelSettings, RoomTypeConfig
from models.user import UserRole
from utils.auth import get_password_hash

# ================================================================
# Scheduler Imports
# ================================================================
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sys
import os

# Add scheduler module to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scheduler import run_daily_tasks  # main scheduler executor


# Global scheduler instance
scheduler = BackgroundScheduler()


def seed_default_admin():
    """Create default admin user if no users exist."""
    db = SessionLocal()
    try:
        existing_user = db.query(User).first()
        if not existing_user:
            admin_user = User(
                email="admin@hotel.com",
                username="admin",
                hashed_password=get_password_hash("admin"),
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created (username: admin, password: admin)")
        else:
            print("✓ Users already exist, skipping admin seed")
    finally:
        db.close()


# ================================================================
# MODERN FASTAPI LIFESPAN HANDLER (REPLACES on_event)
# ================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ============================
    # STARTUP
    # ============================
    print("\n" + "=" * 60)
    print("🚀 HMS Server Starting...")
    print("=" * 60)

    # Seed default admin user
    seed_default_admin()

    # Run tasks immediately (only runs once/day internally)
    print("\n🔍 Checking if daily tasks need to run...")
    run_daily_tasks()

    # Schedule daily execution at 6:00 AM
    scheduler.add_job(
        run_daily_tasks,
        "cron",
        hour=6,
        minute=0,
        id="daily_room_status_update",
        replace_existing=True
    )

    scheduler.start()

    print("\n✅ Scheduler configured:")
    print("   - Daily execution scheduled for 6:00 AM")
    print("   - Startup check completed")
    print("=" * 60 + "\n")

    # Allow app to run
    yield

    # ============================
    # SHUTDOWN
    # ============================
    print("\n⏹️  Shutting down scheduler...")
    if scheduler.running:
        scheduler.shutdown()
    print("✅ Scheduler stopped\n")


# ================================================================
# FastAPI Initialization
# ================================================================
app = FastAPI(
    title="Hotel Management System API",
    description="Backend API for Hotel Management System",
    version="1.0.0",
    lifespan=lifespan  # ✔ modern approach
)


# ================================================================
# Database Initialization
# ================================================================
Base.metadata.create_all(bind=engine)


# ================================================================
# CORS Configuration
# ================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # update later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# Routers
# ================================================================
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(room_types.router)
app.include_router(customers.router)
app.include_router(bookings.router)
app.include_router(billing.router)
app.include_router(reports.router)
app.include_router(settings.router)


# ================================================================
# Health Check Endpoints
# ================================================================
@app.get("/")
async def root():
    return {"message": "Hotel Management System API is running"}

@app.get("/ping")
async def ping():
    return {"status": "success", "message": "pong"}


# ================================================================
# Run Application
# ================================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
