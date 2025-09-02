from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased from 128 to 255
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    settings = db.relationship('UserSetting', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserSetting(db.Model):
    """User-specific settings and configurations."""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.String(64), nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(32), default='string')  # string, int, bool, json
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'setting_key'),)
    
    def __repr__(self):
        return f'<UserSetting {self.user_id}:{self.setting_key}>'

class UserPreference(db.Model):
    """User preferences for dashboard customization."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(32), default='light')  # light, dark, auto
    dashboard_layout = db.Column(db.String(32), default='default')  # default, compact, wide
    sidebar_collapsed = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(64), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference {self.user_id}>'

class AppMetric(db.Model):
    """Application metrics and monitoring data."""
    __tablename__ = 'app_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(64), nullable=False, index=True)
    metric_value = db.Column(db.Float)
    metric_unit = db.Column(db.String(16))
    metric_type = db.Column(db.String(32))  # counter, gauge, histogram
    tags = db.Column(db.JSON)  # Additional metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AppMetric {self.metric_name}:{self.metric_value}>'

class SystemEvent(db.Model):
    """System events and logs."""
    __tablename__ = 'system_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    event_level = db.Column(db.String(16), default='info')  # debug, info, warning, error, critical
    event_message = db.Column(db.Text)
    event_data = db.Column(db.JSON)  # Additional event data
    source = db.Column(db.String(64))  # Component that generated the event
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SystemEvent {self.event_type}:{self.event_level}>'
