#!/usr/bin/env python3
"""
Minimal test to debug where database connection is being attempted.
"""

import os
import sys

print("Step 1: Importing config...")
from config import config
print("✓ Config imported successfully")

print("Step 2: Importing models...")
from models import db, User, UserSetting, UserPreference, AppMetric, SystemEvent
print("✓ Models imported successfully")

print("Step 3: Testing create_app function...")
from app import create_app
print("✓ create_app function imported successfully")

print("Step 4: Creating app...")
app = create_app()
print("✓ App created successfully")

print("All imports and app creation completed successfully!")
