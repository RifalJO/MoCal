"""
Migration script: Add log_detail column to food_logs table
Run this script to update your existing database schema.
"""

import sys
import os
# Add parent directory to path so we can import app.database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.database import settings

# Create database URL
DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

def run_migration():
    """Add log_detail column to food_logs table"""
    print(f"Connecting to database: {settings.DB_NAME}")
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'food_logs' 
                AND column_name = 'log_detail'
            """))
            
            if result.fetchone():
                print("[INFO] Column 'log_detail' already exists!")
                return
            
            # Add the column
            print("Adding 'log_detail' column to 'food_logs' table...")
            conn.execute(text("""
                ALTER TABLE food_logs 
                ADD COLUMN log_detail JSONB
            """))
            conn.commit()
            
            print("[SUCCESS] Migration successful! Column 'log_detail' added.")
            
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()
