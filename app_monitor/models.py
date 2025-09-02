"""
Database Models for App Monitor Dashboard
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import db from the package
from . import db

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    metrics = db.relationship('AppMetric', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserPreference(db.Model):
    """User preferences and settings."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')
    dashboard_layout = db.Column(db.String(50), default='default')
    notifications_enabled = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=30)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference {self.user_id}>'

class AppMetric(db.Model):
    """Application metrics and performance data."""
    __tablename__ = 'app_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, response_time, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='')
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AppMetric {self.metric_type}:{self.value}>'

class SystemEvent(db.Model):
    """System events and logs."""
    __tablename__ = 'system_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # error, warning, info, success
    severity = db.Column(db.String(20), default='info')  # low, medium, high, critical
    message = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), default='system')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_data = db.Column(db.JSON)  # Additional event data
    
    def __repr__(self):
        return f'<SystemEvent {self.event_type}:{self.severity}>'
