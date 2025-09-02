"""
Authentication Blueprint
Handles user login, registration, and logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

from .. import db
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('auth/login.html')
        
        # Try to find user by email or username
        user = User.query.filter(
            (User.email == email) | (User.username == email)
        ).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email/username or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password-confirm')
        agree = request.form.get('agree')
        
        # Validation
        if not all([first_name, last_name, email, password, password_confirm]):
            flash('All fields are required.', 'error')
        elif password != password_confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        elif not agree:
            flash('You must agree to the terms and conditions.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        else:
            # Generate username from email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                # In a real app, you would send a password reset email here
                flash('If an account with that email exists, a password reset link has been sent.', 'info')
            else:
                # Don't reveal if email exists or not for security
                flash('If an account with that email exists, a password reset link has been sent.', 'info')
    
    return render_template('auth/forgot_password.html')
