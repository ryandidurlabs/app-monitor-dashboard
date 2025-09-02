#!/usr/bin/env python3
"""
Main application entry point for App Monitor Dashboard.
This file creates the Flask app instance for local development.
"""

from app_monitor import create_app

# Create the app instance for local development
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
