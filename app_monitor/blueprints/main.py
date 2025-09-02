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
    # Get user's recent metrics
    recent_metrics = AppMetric.query.filter_by(user_id=current_user.id)\
        .order_by(AppMetric.timestamp.desc())\
        .limit(5).all()
    
    # Get recent system events
    recent_events = SystemEvent.query\
        .order_by(SystemEvent.timestamp.desc())\
        .limit(5).all()
    
    # Get user preferences
    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    return render_template('main/dashboard.html',
                         recent_metrics=recent_metrics,
                         recent_events=recent_events,
                         preferences=preferences)

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
