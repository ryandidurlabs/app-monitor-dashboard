import os
from flask import Flask, send_from_directory, abort, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from config import config
from models import db, User, UserSetting, UserPreference, AppMetric, SystemEvent
from datetime import datetime

# Initialize Flask extensions
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints and routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all application routes."""
    
    @app.get("/health")
    def health() -> str:
        return "ok"
    
    @app.get("/")
    def index():
        """Main dashboard page."""
        if current_user.is_authenticated:
            # Get user preferences
            prefs = current_user.preferences.first()
            if prefs:
                theme = prefs.theme
                layout = prefs.dashboard_layout
            else:
                theme = 'light'
                layout = 'default'
            
            # Get recent metrics
            recent_metrics = AppMetric.query.order_by(AppMetric.timestamp.desc()).limit(5).all()
            
            # Get recent system events
            recent_events = SystemEvent.query.order_by(SystemEvent.timestamp.desc()).limit(5).all()
            
            return render_template('dashboard.html', 
                                user=current_user,
                                theme=theme,
                                layout=layout,
                                metrics=recent_metrics,
                                events=recent_events)
        else:
            return send_from_directory("template", "index.html")
    
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        """User login page."""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = request.form.get('remember') == 'on'
            
            # Try to find user by email first, then by username
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User.query.filter_by(username=email).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Invalid email/username or password', 'error')
        
        return send_from_directory("template", "auth-login.html")
    
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        """User registration page."""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            first_name = request.form.get('frist_name')  # Note: template has typo 'frist_name'
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            password_confirm = request.form.get('password-confirm')
            agree = request.form.get('agree')
            
            # Validation
            errors = []
            
            if not first_name or not last_name:
                errors.append('First name and last name are required')
            
            if not email:
                errors.append('Email is required')
            elif User.query.filter_by(email=email).first():
                errors.append('Email already registered')
            
            if not password:
                errors.append('Password is required')
            elif len(password) < 6:
                errors.append('Password must be at least 6 characters')
            elif password != password_confirm:
                errors.append('Passwords do not match')
            
            if not agree:
                errors.append('You must agree to the terms and conditions')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
            else:
                # Create new user
                username = email.split('@')[0]  # Use email prefix as username
                # Ensure username is unique
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_password(password)
                
                # Create default preferences
                prefs = UserPreference(user_id=user.id)
                
                db.session.add(user)
                db.session.add(prefs)
                db.session.commit()
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
        
        return send_from_directory("template", "auth-register.html")
    
    @app.route("/forgot-password", methods=['GET', 'POST'])
    def forgot_password():
        """Password reset request page."""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            
            if not email:
                flash('Please provide your email address', 'error')
            else:
                user = User.query.filter_by(email=email).first()
                if user:
                    # In a real app, you would send a password reset email here
                    flash('If an account with that email exists, a password reset link has been sent.', 'info')
                else:
                    # Don't reveal if email exists or not for security
                    flash('If an account with that email exists, a password reset link has been sent.', 'info')
                
                return redirect(url_for('login'))
        
        return send_from_directory("template", "auth-forgot-password.html")
    
    @app.route("/logout")
    @login_required
    def logout():
        """User logout."""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route("/profile")
    @login_required
    def profile():
        """User profile page."""
        prefs = current_user.preferences.first()
        settings = current_user.settings.all()
        return render_template('profile.html', 
                            user=current_user,
                            preferences=prefs,
                            settings=settings)
    
    @app.route("/api/metrics")
    @login_required
    def api_metrics():
        """API endpoint for application metrics."""
        metrics = AppMetric.query.order_by(AppMetric.timestamp.desc()).limit(100).all()
        return jsonify([{
            'id': m.id,
            'name': m.metric_name,
            'value': m.metric_value,
            'unit': m.metric_unit,
            'type': m.metric_type,
            'tags': m.tags,
            'timestamp': m.timestamp.isoformat()
        } for m in metrics])
    
    @app.route("/api/events")
    @login_required
    def api_events():
        """API endpoint for system events."""
        events = SystemEvent.query.order_by(SystemEvent.timestamp.desc()).limit(100).all()
        return jsonify([{
            'id': e.id,
            'type': e.event_type,
            'level': e.event_level,
            'message': e.event_message,
            'data': e.event_data,
            'source': e.source,
            'timestamp': e.timestamp.isoformat()
        } for e in events])
    
    @app.route("/api/preferences", methods=['GET', 'POST'])
    @login_required
    def api_preferences():
        """API endpoint for user preferences."""
        if request.method == 'POST':
            data = request.get_json()
            
            prefs = current_user.preferences.first()
            if not prefs:
                prefs = UserPreference(user_id=current_user.id)
                db.session.add(prefs)
            
            # Update preferences
            for key, value in data.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)
            
            db.session.commit()
            return jsonify({'status': 'success'})
        
        # GET request
        prefs = current_user.preferences.first()
        if prefs:
            return jsonify({
                'theme': prefs.theme,
                'dashboard_layout': prefs.dashboard_layout,
                'sidebar_collapsed': prefs.sidebar_collapsed,
                'notifications_enabled': prefs.notifications_enabled,
                'language': prefs.language,
                'timezone': prefs.timezone
            })
        else:
            return jsonify({})
    
    # Serve static assets (CSS, JS, images)
    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        """Serve static assets from the template/assets directory."""
        return send_from_directory("template/assets", filename)
    
    @app.get("/<string:page>")
    @app.get("/<string:page>.html")
    def page_router(page: str):
        """Route for other HTML pages."""
        # Only allow single-segment pages, to avoid catching static assets
        filename = f"{page}.html"
        file_path = os.path.join("template", filename)
        if os.path.isfile(file_path):
            return send_from_directory("template", filename)
        abort(404)
    
    @app.get("/pages")
    def list_pages():
        """Simple sitemap of available top-level pages."""
        try:
            entries = []
            for name in sorted(os.listdir("template")):
                if not name.lower().endswith(".html"):
                    continue
                if name.startswith("errors-"):
                    continue
                entries.append(name)
            if not entries:
                return "No pages found", 200
            links = "".join(
                f"<li><a href='/{n[:-5]}'>{n}</a></li>" for n in entries
            )
            return f"<h1>Pages</h1><ul>{links}</ul>", 200
        except Exception:
            abort(500)
    
    @app.errorhandler(404)
    def not_found(_):
        """Try to serve themed 404 page if available."""
        custom_404 = os.path.join("template", "errors-404.html")
        if os.path.isfile(custom_404):
            return send_from_directory("template", "errors-404.html"), 404
        return "Not Found", 404

# Create the app instance only when running directly
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
