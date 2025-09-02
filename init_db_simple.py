#!/usr/bin/env python3
"""
Simple database initialization script for App Monitor Dashboard.
This script directly connects to the database without importing the full Flask app.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import db, User, UserSetting, UserPreference, AppMetric, SystemEvent
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database with tables and sample data."""
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
        
        # Create all tables
        print("Creating database tables...")
        db.metadata.create_all(engine)
        print("✓ Database tables created successfully!")
        
        # Check if we already have users
        existing_users = session.query(User).first()
        if existing_users:
            print("Database already contains data. Skipping sample data creation.")
            return
        
        print("Adding sample data...")
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@appmonitor.com',
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin_user.set_password('admin123')
        session.add(admin_user)
        
        # Create regular user
        regular_user = User(
            username='user',
            email='user@appmonitor.com',
            first_name='Regular',
            last_name='User',
            is_admin=False,
            is_active=True,
            created_at=datetime.utcnow()
        )
        regular_user.set_password('user123')
        session.add(regular_user)
        
        # Commit users first to get their IDs
        session.commit()
        
        # Create user preferences
        admin_prefs = UserPreference(
            user_id=admin_user.id,
            theme='dark',
            dashboard_layout='wide',
            sidebar_collapsed=False,
            notifications_enabled=True,
            language='en',
            timezone='UTC'
        )
        session.add(admin_prefs)
        
        user_prefs = UserPreference(
            user_id=regular_user.id,
            theme='light',
            dashboard_layout='default',
            sidebar_collapsed=True,
            notifications_enabled=True,
            language='en',
            timezone='America/New_York'
        )
        session.add(user_prefs)
        
        # Create sample app metrics
        sample_metrics = [
            AppMetric(
                metric_name='cpu_usage',
                metric_value=45.2,
                metric_unit='%',
                metric_type='gauge',
                tags={'server': 'web-01', 'environment': 'production'},
                timestamp=datetime.utcnow()
            ),
            AppMetric(
                metric_name='memory_usage',
                metric_value=78.5,
                metric_unit='%',
                metric_type='gauge',
                tags={'server': 'web-01', 'environment': 'production'},
                timestamp=datetime.utcnow()
            ),
            AppMetric(
                metric_name='response_time',
                metric_value=125.3,
                metric_unit='ms',
                metric_type='histogram',
                tags={'endpoint': '/api/users', 'method': 'GET'},
                timestamp=datetime.utcnow()
            ),
            AppMetric(
                metric_name='requests_per_second',
                metric_value=150.0,
                metric_unit='req/s',
                metric_type='counter',
                tags={'endpoint': '/', 'method': 'GET'},
                timestamp=datetime.utcnow()
            )
        ]
        
        for metric in sample_metrics:
            session.add(metric)
        
        # Create sample system events
        sample_events = [
            SystemEvent(
                event_type='app_startup',
                event_level='info',
                event_message='Application started successfully',
                event_data={'version': '1.0.0', 'environment': 'production'},
                source='app',
                timestamp=datetime.utcnow()
            ),
            SystemEvent(
                event_type='database_connection',
                event_level='info',
                event_message='Database connection established',
                event_data={'database': 'postgresql', 'host': 'localhost'},
                source='database',
                timestamp=datetime.utcnow()
            ),
            SystemEvent(
                event_type='user_login',
                event_level='info',
                event_message='User logged in successfully',
                event_data={'username': 'admin', 'ip': '192.168.1.100'},
                source='auth',
                timestamp=datetime.utcnow()
            )
        ]
        
        for event in sample_events:
            session.add(event)
        
        # Commit all changes
        session.commit()
        print("✓ Sample data added successfully!")
        
        print("\nDatabase initialization completed!")
        print(f"Admin user: admin / admin123")
        print(f"Regular user: user / user123")
        
        session.close()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init_db()
