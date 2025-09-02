#!/usr/bin/env python3
"""
WSGI entry point for Heroku deployment.
This file creates the Flask app when called by gunicorn.
"""

from app_monitor import create_app

# Create the app instance for WSGI deployment
app = create_app()

if __name__ == "__main__":
    app.run()
