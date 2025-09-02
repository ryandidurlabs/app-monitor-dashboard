"""
API Blueprint
Handles API endpoints for metrics, events, and preferences
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from .. import db
from ..models import AppMetric, SystemEvent, UserPreference

api_bp = Blueprint('api', __name__)

@api_bp.route('/metrics', methods=['GET', 'POST'])
@login_required
def metrics():
    """Handle metrics API endpoints."""
    if request.method == 'GET':
        # Check if this is an API request (JSON) or web page request
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            # API request - return JSON
            metrics = AppMetric.query.filter_by(user_id=current_user.id)\
                .order_by(AppMetric.timestamp.desc())\
                .limit(100).all()
            
            return jsonify({
                'success': True,
                'data': [{
                    'id': m.id,
                    'metric_type': m.metric_type,
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'description': m.description
                } for m in metrics]
            })
        else:
            # Web page request - render template
            return render_template('api/metrics.html')
    
    elif request.method == 'POST':
        # Create new metric
        data = request.get_json()
        
        if not data or 'metric_type' not in data or 'value' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        metric = AppMetric(
            user_id=current_user.id,
            metric_type=data['metric_type'],
            value=data['value'],
            description=data.get('description', ''),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': metric.id,
                'metric_type': metric.metric_type,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat()
            }
        }), 201

@api_bp.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    """Handle system events API endpoints."""
    if request.method == 'GET':
        # Get recent system events
        events = SystemEvent.query\
            .order_by(SystemEvent.timestamp.desc())\
            .limit(50).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': e.id,
                'event_type': e.event_type,
                'severity': e.severity,
                'message': e.message,
                'timestamp': e.timestamp.isoformat(),
                'source': e.source
            } for e in events]
        })
    
    elif request.method == 'POST':
        # Create new system event
        data = request.get_json()
        
        if not data or 'event_type' not in data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        event = SystemEvent(
            event_type=data['event_type'],
            severity=data.get('severity', 'info'),
            message=data['message'],
            source=data.get('source', 'user'),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': event.id,
                'event_type': event.event_type,
                'severity': event.severity,
                'message': event.message,
                'timestamp': event.timestamp.isoformat()
            }
        }), 201

@api_bp.route('/preferences', methods=['GET', 'PUT'])
@login_required
def preferences():
    """Handle user preferences API endpoints."""
    if request.method == 'GET':
        # Get user preferences
        preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        if not preferences:
            # Create default preferences if none exist
            preferences = UserPreference(
                user_id=current_user.id,
                theme='light',
                dashboard_layout='default',
                notifications_enabled=True,
                refresh_interval=30
            )
            db.session.add(preferences)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'theme': preferences.theme,
                'dashboard_layout': preferences.dashboard_layout,
                'notifications_enabled': preferences.notifications_enabled,
                'refresh_interval': preferences.refresh_interval
            }
        })
    
    elif request.method == 'PUT':
        # Update user preferences
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        if not preferences:
            preferences = UserPreference(user_id=current_user.id)
            db.session.add(preferences)
        
        # Update allowed fields
        allowed_fields = ['theme', 'dashboard_layout', 'notifications_enabled', 'refresh_interval']
        for field in allowed_fields:
            if field in data:
                setattr(preferences, field, data[field])
        
        preferences.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'theme': preferences.theme,
                'dashboard_layout': preferences.dashboard_layout,
                'notifications_enabled': preferences.notifications_enabled,
                'refresh_interval': preferences.refresh_interval
            }
        })
