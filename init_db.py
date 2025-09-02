#!/usr/bin/env python3
"""
Database initialization script for App Monitor Dashboard.
Run this script to create all database tables and add sample data.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, UserSetting, UserPreference, AppMetric, SystemEvent
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if we already have users
        if User.query.first():
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
        db.session.add(admin_user)
        
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
        db.session.add(regular_user)
        
        # Commit users first to get their IDs
        db.session.commit()
        
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
        db.session.add(admin_prefs)
        
        user_prefs = UserPreference(
            user_id=regular_user.id,
            theme='light',
            dashboard_layout='default',
            sidebar_collapsed=True,
            notifications_enabled=True,
            language='en',
            timezone='America/New_York'
        )
        db.session.add(user_prefs)
        
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
            db.session.add(metric)
        
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
            db.session.add(event)
        
        # Commit all changes
        db.session.commit()
        print("✓ Sample data added successfully!")
        
        print("\nDatabase initialization completed!")
        print(f"Admin user: admin / admin123")
        print(f"Regular user: user / user123")

if __name__ == '__main__':
    init_db()
