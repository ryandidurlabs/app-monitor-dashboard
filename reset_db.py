#!/usr/bin/env python3
"""
Database reset script for App Monitor Dashboard.
This script drops all tables and recreates them with the correct schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import db, User, UserSetting, UserPreference, AppMetric, SystemEvent

def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        return
    
    # Fix Heroku's postgres:// URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to database: {database_url[:50]}...")
    
    try:
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        result = session.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
        
        # Drop all tables
        print("Dropping all existing tables...")
        db.metadata.drop_all(engine)
        print("✓ All tables dropped successfully!")
        
        # Create all tables with new schema
        print("Creating database tables with new schema...")
        db.metadata.create_all(engine)
        print("✓ Database tables created successfully!")
        
        session.close()
        print("Database reset completed!")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    reset_db()
