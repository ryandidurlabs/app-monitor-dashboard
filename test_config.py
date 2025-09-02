#!/usr/bin/env python3
"""
Test configuration script to debug database URL issues.
"""

import os
from config import config

def test_config():
    """Test the configuration loading."""
    print("Testing configuration...")
    
    # Check environment variables
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    # Load production config
    prod_config = config['production']
    print(f"Production config class: {prod_config}")
    
    # Check if init_app method exists
    if hasattr(prod_config, 'init_app'):
        print("✓ Production config has init_app method")
    else:
        print("✗ Production config missing init_app method")
    
    # Create a dummy app to test config
    class DummyApp:
        def __init__(self):
            self.config = {}
    
    dummy_app = DummyApp()
    prod_config.init_app(dummy_app)
    
    print(f"Final DATABASE_URL: {prod_config.SQLALCHEMY_DATABASE_URI}")
    
    if prod_config.SQLALCHEMY_DATABASE_URI and prod_config.SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        print("✓ Database URL is correctly formatted as postgresql://")
    else:
        print("✗ Database URL is NOT correctly formatted")

if __name__ == '__main__':
    test_config()
