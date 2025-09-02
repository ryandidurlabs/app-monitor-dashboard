#!/usr/bin/env python3
"""
Database initialization script for the new package structure.
This script creates all database tables and populates them with sample data.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_monitor import create_app, db
from app_monitor.models import User, UserPreference, AppMetric, SystemEvent

def init_database():
    """Initialize the database with tables and sample data."""
    print("Creating Flask app...")
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Creating sample users...")
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@appmonitor.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create regular user
        regular_user = User(
            username='user',
            email='user@appmonitor.com',
            first_name='Regular',
            last_name='User',
            is_active=True,
            is_admin=False
        )
        regular_user.set_password('user123')
        db.session.add(regular_user)
        
        # Commit users to get their IDs
        db.session.commit()
        
        print("Creating user preferences...")
        
        # Create preferences for admin user
        admin_prefs = UserPreference(
            user_id=admin_user.id,
            theme='dark',
            dashboard_layout='wide',
            notifications_enabled=True,
            refresh_interval=30
        )
        db.session.add(admin_prefs)
        
        # Create preferences for regular user
        user_prefs = UserPreference(
            user_id=regular_user.id,
            theme='light',
            dashboard_layout='default',
            notifications_enabled=True,
            refresh_interval=60
        )
        db.session.add(user_prefs)
        
        print("Creating sample metrics...")
        
        # Create sample metrics for admin user
        for i in range(5):
            metric = AppMetric(
                user_id=admin_user.id,
                metric_type='cpu_usage',
                value=75.0 + i * 5,
                unit='%',
                description=f'CPU usage sample {i+1}',
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db.session.add(metric)
        
        # Create sample metrics for regular user
        for i in range(3):
            metric = AppMetric(
                user_id=regular_user.id,
                metric_type='memory_usage',
                value=60.0 + i * 10,
                unit='%',
                description=f'Memory usage sample {i+1}',
                timestamp=datetime.utcnow() - timedelta(hours=i*2)
            )
            db.session.add(metric)
        
        print("Creating sample system events...")
        
        # Create sample system events
        events = [
            ('system_startup', 'low', 'System started successfully', 'system'),
            ('user_login', 'low', 'User admin logged in', 'auth'),
            ('database_backup', 'medium', 'Database backup completed', 'system'),
            ('error_log', 'high', 'Application error detected', 'system'),
            ('update_available', 'low', 'System update available', 'system')
        ]
        
        for event_type, severity, message, source in events:
            event = SystemEvent(
                event_type=event_type,
                severity=severity,
                message=message,
                source=source,
                timestamp=datetime.utcnow() - timedelta(hours=len(events)-events.index((event_type, severity, message, source)))
            )
            db.session.add(event)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print(f"Created {User.query.count()} users")
        print(f"Created {UserPreference.query.count()} user preferences")
        print(f"Created {AppMetric.query.count()} metrics")
        print(f"Created {SystemEvent.query.count()} system events")
        
        print("\nSample login credentials:")
        print("Admin: admin@appmonitor.com / admin123")
        print("User: user@appmonitor.com / user123")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
