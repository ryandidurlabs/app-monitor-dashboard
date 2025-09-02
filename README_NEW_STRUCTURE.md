# App Monitor Dashboard - New Structure

This document describes the new, restructured Flask application that follows Flask best practices and uses a proper package structure.

## New Structure Overview

The application has been completely restructured from the old monolithic approach to a proper Flask package structure:

```
app-monitor/
├── __init__.py              # Main package initialization and app factory
├── config.py                # Configuration classes
├── models.py                # Database models
├── blueprints/              # Route organization
│   ├── __init__.py
│   ├── auth.py             # Authentication routes (login, register, logout)
│   ├── main.py             # Main routes (dashboard, profile, index)
│   └── api.py              # API endpoints (metrics, events, preferences)
├── templates/               # Jinja2 templates (Flask standard)
│   ├── base.html           # Base template with common structure
│   ├── auth/               # Authentication templates
│   │   ├── login.html
│   │   ├── register.html
│   │   └── forgot_password.html
│   └── main/               # Main application templates
│       ├── index.html      # Landing page
│       ├── dashboard.html  # User dashboard
│       └── profile.html    # User profile
├── static/                  # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── img/
│   └── bundles/
├── app_new.py              # Local development entry point
├── wsgi_new.py             # Heroku deployment entry point
├── Procfile.new            # New Heroku Procfile
├── requirements_new.txt     # Updated dependencies
└── init_db_new.py          # Database initialization script
```

## Key Improvements

### 1. **Proper Flask Package Structure**
- Uses `__init__.py` for app factory pattern
- Blueprint-based route organization
- Proper separation of concerns

### 2. **Template Organization**
- Templates now use Flask's standard `templates/` directory
- Proper template inheritance with `base.html`
- Organized by feature (auth, main)

### 3. **Static Asset Management**
- Static files moved to `static/` directory (Flask standard)
- Proper URL generation using `url_for('static', filename='...')`
- All CSS, JS, and images properly organized

### 4. **Blueprint Architecture**
- **Auth Blueprint**: Handles all authentication (login, register, logout, forgot password)
- **Main Blueprint**: Handles main application pages (dashboard, profile, index)
- **API Blueprint**: Handles all API endpoints (metrics, events, preferences)

### 5. **Improved Models**
- Cleaner database model definitions
- Better relationships and constraints
- Proper field types and lengths

## How to Use the New Structure

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements_new.txt
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=development
   export DATABASE_URL=your_database_url
   ```

3. **Initialize database:**
   ```bash
   python init_db_new.py
   ```

4. **Run the application:**
   ```bash
   python app_new.py
   ```

### Heroku Deployment

1. **Update Procfile:**
   ```bash
   cp Procfile.new Procfile
   ```

2. **Update requirements.txt:**
   ```bash
   cp requirements_new.txt requirements.txt
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Restructure application with proper Flask architecture"
   git push heroku master
   ```

4. **Initialize database on Heroku:**
   ```bash
   heroku run python init_db_new.py
   ```

## Migration from Old Structure

### Files to Replace:
- `app.py` → `app_new.py` (for local development)
- `wsgi.py` → `wsgi_new.py` (for Heroku)
- `Procfile` → `Procfile.new`
- `requirements.txt` → `requirements_new.txt`

### Template Changes:
- All templates now use `{{ url_for('blueprint.route_name') }}` instead of hardcoded paths
- Static assets use `{{ url_for('static', filename='...') }}`
- Proper template inheritance with `{% extends "base.html" %}`

### Route Changes:
- Authentication routes: `/login`, `/register`, `/logout`, `/forgot-password`
- Main routes: `/`, `/dashboard`, `/profile`
- API routes: `/api/metrics`, `/api/events`, `/api/preferences`

## Benefits of New Structure

1. **Maintainability**: Clear separation of concerns and organized code
2. **Scalability**: Easy to add new features and blueprints
3. **Testing**: Better structure for unit and integration tests
4. **Deployment**: Cleaner deployment process
5. **Standards**: Follows Flask best practices and conventions

## Sample Login Credentials

After running `init_db_new.py`, you can use these credentials:

- **Admin User**: `admin@appmonitor.com` / `admin123`
- **Regular User**: `user@appmonitor.com` / `user123`

## Next Steps

1. Test the new structure locally
2. Update your deployment process
3. Consider adding more blueprints for additional features
4. Implement proper error handling and logging
5. Add comprehensive testing

The new structure provides a solid foundation for building a professional, scalable Flask application that follows industry best practices.
