"""
Migration script to add gst_number column to hotel_settings table.
Run this script to update your existing database.

Usage:
    python migrations/add_gst_number.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import database
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config import settings

def migrate():
    """Add gst_number column to hotel_settings table"""
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(hotel_settings)"))
            columns = [row[1] for row in result.fetchall()]

            if 'gst_number' in columns:
                print("✓ gst_number column already exists in hotel_settings table")
                return

            # Add the column
            conn.execute(text("ALTER TABLE hotel_settings ADD COLUMN gst_number VARCHAR"))
            conn.commit()
            print("✅ Successfully added gst_number column to hotel_settings table")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("Running database migration: Add GST Number")
    print("=" * 50)
    migrate()
    print("=" * 50)
    print("Migration completed!")
