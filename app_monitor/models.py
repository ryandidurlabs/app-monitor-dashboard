"""
Database Models for App Monitor Dashboard
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

# Import db from the package
from . import db

class Company(db.Model):
    """Company/Organization model."""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    employee_count = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='company', cascade='all, delete-orphan')
    sso_configs = db.relationship('SSOConfiguration', backref='company', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.name}>'

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')  # user, admin, super_admin
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
    
    def is_super_admin(self):
        """Check if user is a super admin."""
        return self.role == 'super_admin'
    
    def can_manage_company(self, company_id):
        """Check if user can manage a specific company."""
        return self.is_super_admin() or (self.company_id == company_id and self.is_admin)
    
    def __repr__(self):
        return f'<User {self.username}>'

class SSOConfiguration(db.Model):
    """SSO provider configuration for companies."""
    __tablename__ = 'sso_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    provider_name = db.Column(db.String(50), nullable=False)  # entra_id, okta, auth0, etc.
    display_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    config_data = db.Column(db.JSON)  # Provider-specific configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SSOConfiguration {self.provider_name} for {self.company_id}>'

class EntraIntegration(db.Model):
    """Microsoft Entra ID (Azure AD) integration details."""
    __tablename__ = 'entra_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    sso_config_id = db.Column(db.Integer, db.ForeignKey('sso_configurations.id'), nullable=False)
    tenant_id = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.String(100), nullable=False)
    client_secret = db.Column(db.String(500), nullable=False)  # Encrypted
    api_key = db.Column(db.String(500), nullable=False)  # Encrypted
    permissions_granted = db.Column(db.JSON)  # List of granted permissions
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(50), default='pending')  # pending, active, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sso_config = db.relationship('SSOConfiguration', backref='entra_integration')
    
    def __repr__(self):
        return f'<EntraIntegration {self.tenant_id}>'

class SSOApplication(db.Model):
    """SSO applications discovered from Entra ID."""
    __tablename__ = 'sso_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    entra_app_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(200), nullable=False)
    app_type = db.Column(db.String(100))  # web, mobile, desktop, etc.
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='sso_applications')
    
    def __repr__(self):
        return f'<SSOApplication {self.name}>'

class UserActivity(db.Model):
    """User activity logs from SSO applications."""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('sso_applications.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # login, logout, access, etc.
    timestamp = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(200))
    success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(500))
    metadata = db.Column(db.JSON)  # Additional activity data
    
    # Relationships
    company = db.relationship('Company', backref='user_activities')
    user = db.relationship('User', backref='activities')
    app = db.relationship('SSOApplication', backref='user_activities')
    
    def __repr__(self):
        return f'<UserActivity {self.user_id} {self.activity_type} {self.timestamp}>'

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
