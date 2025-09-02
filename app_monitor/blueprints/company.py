"""
Company and SSO Management Blueprint
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import json

from ..models import db, Company, User, SSOConfiguration, EntraIntegration, SSOApplication
from ..utils.entra_client import EntraClient

company_bp = Blueprint('company', __name__)

@company_bp.route('/company/setup', methods=['GET', 'POST'])
@login_required
def company_setup():
    """Company setup wizard for new organizations."""
    if request.method == 'POST':
        data = request.form
        
        # Create company
        company = Company(
            name=data['company_name'],
            domain=data['company_domain'],
            industry=data.get('industry'),
            employee_count=int(data.get('employee_count', 0)) if data.get('employee_count') else None
        )
        db.session.add(company)
        db.session.flush()  # Get the company ID
        
        # Update current user to be company admin
        current_user.company_id = company.id
        current_user.role = 'admin'
        current_user.is_admin = True
        
        # Create SSO configuration
        sso_config = SSOConfiguration(
            company_id=company.id,
            provider_name='entra_id',
            display_name='Microsoft Entra ID',
            config_data={
                'tenant_id': data.get('tenant_id'),
                'client_id': data.get('client_id'),
                'client_secret': data.get('client_secret'),
                'api_key': data.get('api_key')
            }
        )
        db.session.add(sso_config)
        db.session.flush()
        
        # Create Entra integration
        entra_integration = EntraIntegration(
            sso_config_id=sso_config.id,
            tenant_id=data.get('tenant_id'),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            api_key=data.get('api_key'),
            permissions_granted=[],
            sync_status='pending'
        )
        db.session.add(entra_integration)
        
        db.session.commit()
        flash('Company setup completed successfully!', 'success')
        return redirect(url_for('company.entra_setup'))
    
    return render_template('company/setup.html')

@company_bp.route('/company/entra-setup')
@login_required
def entra_setup():
    """Entra ID setup instructions and configuration."""
    if not current_user.company_id:
        flash('Please complete company setup first.', 'error')
        return redirect(url_for('company.company_setup'))
    
    company = Company.query.get(current_user.company_id)
    
    # Check actual configuration status
    sso_config = SSOConfiguration.query.filter_by(
        company_id=company.id, 
        provider_name='entra_id'
    ).first()
    
    entra_integration = None
    if sso_config:
        entra_integration = EntraIntegration.query.filter_by(
            sso_config_id=sso_config.id
        ).first()
    
    # Determine setup status
    setup_status = {
        'company_setup': True,  # Company exists
        'entra_config': bool(sso_config and entra_integration and entra_integration.tenant_id),
        'permissions': bool(entra_integration and entra_integration.permissions_granted),
        'sync_data': bool(entra_integration and entra_integration.sync_status == 'active')
    }
    
    return render_template('company/entra_setup.html', 
                         company=company,
                         setup_status=setup_status,
                         sso_config=sso_config,
                         entra_integration=entra_integration)

@company_bp.route('/company/dashboard')
@login_required
def company_dashboard():
    """Company dashboard showing SSO applications and activity."""
    if not current_user.company_id:
        flash('Please complete company setup first.', 'error')
        return redirect(url_for('company.company_setup'))
    
    company = Company.query.get(current_user.company_id)
    sso_apps = SSOApplication.query.filter_by(company_id=company.id).all()
    
    # Get recent activity
    recent_activities = UserActivity.query.filter_by(company_id=company.id)\
        .order_by(UserActivity.timestamp.desc()).limit(20).all()
    
    return render_template('company/dashboard.html', 
                         company=company, 
                         sso_apps=sso_apps,
                         recent_activities=recent_activities)

@company_bp.route('/company/sso-apps')
@login_required
def sso_applications():
    """List of SSO applications for the company."""
    if not current_user.company_id:
        flash('Please complete company setup first.', 'error')
        return redirect(url_for('company.company_setup'))
    
    company = Company.query.get(current_user.company_id)
    sso_apps = SSOApplication.query.filter_by(company_id=company.id).all()
    
    return render_template('company/sso_applications.html', 
                         company=company, 
                         sso_apps=sso_apps)

@company_bp.route('/company/sync-entra', methods=['POST'])
@login_required
def sync_entra():
    """Sync with Entra ID to discover applications and users."""
    if not current_user.company_id:
        return jsonify({'error': 'Company not set up'}), 400
    
    if not current_user.can_manage_company(current_user.company_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    try:
        company = Company.query.get(current_user.company_id)
        sso_config = SSOConfiguration.query.filter_by(
            company_id=company.id, 
            provider_name='entra_id'
        ).first()
        
        if not sso_config:
            return jsonify({'error': 'Entra ID not configured'}), 400
        
        entra_integration = EntraIntegration.query.filter_by(
            sso_config_id=sso_config.id
        ).first()
        
        if not entra_integration:
            return jsonify({'error': 'Entra integration not found'}), 400
        
        # Initialize Entra client and sync
        entra_client = EntraClient(
            tenant_id=entra_integration.tenant_id,
            client_id=entra_integration.client_id,
            client_secret=entra_integration.client_secret
        )
        
        # Sync applications
        apps = entra_client.get_applications()
        for app_data in apps:
            existing_app = SSOApplication.query.filter_by(
                company_id=company.id,
                entra_app_id=app_data['id']
            ).first()
            
            if not existing_app:
                app = SSOApplication(
                    company_id=company.id,
                    entra_app_id=app_data['id'],
                    name=app_data['displayName'],
                    app_type=app_data.get('signInAudience', 'web'),
                    is_active=app_data.get('enabled', True)
                )
                db.session.add(app)
        
        # Update sync status
        entra_integration.last_sync = datetime.utcnow()
        entra_integration.sync_status = 'active'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Synced {len(apps)} applications from Entra ID'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/company/test-connection', methods=['POST'])
@login_required
def test_entra_connection():
    """Test the Entra ID connection."""
    if not current_user.company_id:
        return jsonify({'error': 'Company not set up'}), 400
    
    if not current_user.can_manage_company(current_user.company_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    try:
        company = Company.query.get(current_user.company_id)
        sso_config = SSOConfiguration.query.filter_by(
            company_id=company.id, 
            provider_name='entra_id'
        ).first()
        
        if not sso_config:
            return jsonify({'error': 'Entra ID not configured'}), 400
        
        entra_integration = EntraIntegration.query.filter_by(
            sso_config_id=sso_config.id
        ).first()
        
        if not entra_integration:
            return jsonify({'error': 'Entra integration not found'}), 400
        
        # Test connection by trying to get applications
        entra_client = EntraClient(
            tenant_id=entra_integration.tenant_id,
            client_id=entra_integration.client_id,
            client_secret=entra_integration.client_secret
        )
        
        # Try to get applications to test connection
        apps = entra_client.get_applications()
        
        return jsonify({
            'success': True,
            'message': f'Connection successful! Found {len(apps)} applications.',
            'app_count': len(apps)
        })
        
    except Exception as e:
        return jsonify({'error': f'Connection failed: {str(e)}'}), 500

@company_bp.route('/company/users')
@login_required
def company_users():
    """Manage users within the company."""
    if not current_user.company_id:
        flash('Please complete company setup first.', 'error')
        return redirect(url_for('company.company_setup'))
    
    if not current_user.can_manage_company(current_user.company_id):
        flash('Insufficient permissions to view users.', 'error')
        return redirect(url_for('company.company_dashboard'))
    
    company = Company.query.get(current_user.company_id)
    users = User.query.filter_by(company_id=company.id).all()
    
    return render_template('company/users.html', company=company, users=users)

@company_bp.route('/company/add-user', methods=['POST'])
@login_required
def add_user():
    """Add a new user to the company."""
    if not current_user.company_id:
        return jsonify({'error': 'Company not set up'}), 400
    
    if not current_user.can_manage_company(current_user.company_id):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400
    
    # Create new user
    user = User(
        company_id=current_user.company_id,
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'user'),
        is_admin=data.get('is_admin', False)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User added successfully',
        'user_id': user.id
    })
