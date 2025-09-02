"""
Main Blueprint
Handles dashboard, index page, and profile functionality
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from .. import db
from ..models import User, UserPreference, AppMetric, SystemEvent

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page."""
    # Get user's company and related data
    company = None
    sso_apps = []
    recent_activities = []
    
    if hasattr(current_user, 'company') and current_user.company:
        company = current_user.company
        
        # Get SSO applications for the company
        from ..models import SSOApplication
        sso_apps = SSOApplication.query.filter_by(company_id=company.id).all()
        
        # Get recent user activities
        from ..models import UserActivity
        recent_activities = UserActivity.query.filter_by(company_id=company.id)\
            .order_by(UserActivity.timestamp.desc()).limit(20).all()
    
    # Get recent metrics and events for the user
    metrics = AppMetric.query.filter_by(user_id=current_user.id)\
        .order_by(AppMetric.timestamp.desc()).limit(8).all()
    
    events = SystemEvent.query.order_by(SystemEvent.timestamp.desc()).limit(10).all()
    
    return render_template('main/dashboard.html', 
                         company=company,
                         sso_apps=sso_apps,
                         recent_activities=recent_activities,
                         metrics=metrics,
                         events=events)

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    return render_template('main/profile.html', preferences=preferences)

@main_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    
    if not all([first_name, last_name, email]):
        flash('All fields are required.', 'error')
        return redirect(url_for('main.profile'))
    
    # Check if email is already taken by another user
    existing_user = User.query.filter(
        User.email == email,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        flash('Email already taken by another user.', 'error')
        return redirect(url_for('main.profile'))
    
    # Update user info
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    current_user.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('main.profile'))
