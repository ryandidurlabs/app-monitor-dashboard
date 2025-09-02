#!/usr/bin/env python3
"""
Enhanced Database Initialization Script
Creates all tables and populates with sample data for the enhanced SSO monitoring system
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_monitor import create_app, db
from app_monitor.models import (
    Company, User, UserPreference, AppMetric, SystemEvent,
    SSOConfiguration, EntraIntegration, SSOApplication, UserActivity
)

def init_database():
    """Initialize the database with all tables and sample data."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating database tables...")
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create sample companies
        print("🏢 Creating sample companies...")
        
        companies = [
            Company(
                name="TechCorp Solutions",
                domain="techcorp.com",
                industry="technology",
                employee_count=250,
                is_active=True
            ),
            Company(
                name="HealthCare Systems",
                domain="healthcare-sys.com",
                industry="healthcare",
                employee_count=1200,
                is_active=True
            ),
            Company(
                name="Global Finance Group",
                domain="globalfinance.com",
                industry="finance",
                employee_count=5000,
                is_active=True
            )
        ]
        
        for company in companies:
            db.session.add(company)
        
        db.session.flush()  # Get company IDs
        
        print(f"✅ Created {len(companies)} companies")
        
        # Create sample users for each company
        print("👥 Creating sample users...")
        
        users = []
        for i, company in enumerate(companies):
            # Create admin user for each company
            admin_user = User(
                company_id=company.id,
                username=f"admin@{company.domain}",
                email=f"admin@{company.domain}",
                first_name="Admin",
                last_name="User",
                password_hash="",  # Will be set below
                role="admin",
                is_active=True,
                is_admin=True
            )
            admin_user.set_password("admin123")
            users.append(admin_user)
            
            # Create regular users
            for j in range(random.randint(3, 8)):
                user = User(
                    company_id=company.id,
                    username=f"user{j+1}@{company.domain}",
                    email=f"user{j+1}@{company.domain}",
                    first_name=f"User{j+1}",
                    last_name="Employee",
                    password_hash="",
                    role="user",
                    is_active=True,
                    is_admin=False
                )
                user.set_password("user123")
                users.append(user)
        
        for user in users:
            db.session.add(user)
        
        db.session.flush()
        
        print(f"✅ Created {len(users)} users")
        
        # Create SSO configurations for each company
        print("🔐 Creating SSO configurations...")
        
        sso_configs = []
        for company in companies:
            sso_config = SSOConfiguration(
                company_id=company.id,
                provider_name="entra_id",
                display_name="Microsoft Entra ID",
                is_active=True,
                config_data={
                    "tenant_id": f"tenant-{company.id}-{random.randint(1000, 9999)}",
                    "client_id": f"client-{company.id}-{random.randint(1000, 9999)}",
                    "client_secret": f"secret-{company.id}-{random.randint(1000, 9999)}",
                    "api_key": f"api-{company.id}-{random.randint(1000, 9999)}"
                }
            )
            sso_configs.append(sso_config)
            db.session.add(sso_config)
        
        db.session.flush()
        
        print(f"✅ Created {len(sso_configs)} SSO configurations")
        
        # Create Entra integrations
        print("🔗 Creating Entra integrations...")
        
        for sso_config in sso_configs:
            entra_integration = EntraIntegration(
                sso_config_id=sso_config.id,
                tenant_id=sso_config.config_data["tenant_id"],
                client_id=sso_config.config_data["client_id"],
                client_secret=sso_config.config_data["client_secret"],
                api_key=sso_config.config_data["api_key"],
                permissions_granted=[
                    "Application.Read.All",
                    "User.Read.All",
                    "AuditLog.Read.All",
                    "Directory.Read.All"
                ],
                last_sync=datetime.utcnow() - timedelta(hours=2),
                sync_status="active"
            )
            db.session.add(entra_integration)
        
        print("✅ Created Entra integrations")
        
        # Create sample SSO applications for each company
        print("📱 Creating sample SSO applications...")
        
        app_names = [
            "Microsoft 365", "Salesforce", "Slack", "Zoom", "GitHub",
            "Jira", "Confluence", "Box", "Dropbox", "Google Workspace",
            "AWS Console", "Azure Portal", "Okta", "OneLogin", "PingOne"
        ]
        
        for company in companies:
            # Create 5-10 applications per company
            num_apps = random.randint(5, 10)
            company_apps = random.sample(app_names, num_apps)
            
            for app_name in company_apps:
                app = SSOApplication(
                    company_id=company.id,
                    entra_app_id=f"app-{company.id}-{random.randint(1000, 9999)}",
                    name=app_name,
                    app_type=random.choice(["web", "mobile", "desktop"]),
                    is_active=random.choice([True, True, True, False]),  # 75% active
                    last_activity=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
                )
                db.session.add(app)
        
        print("✅ Created sample SSO applications")
        
        # Create user preferences
        print("⚙️ Creating user preferences...")
        
        for user in users:
            preference = UserPreference(
                user_id=user.id,
                theme=random.choice(["light", "dark"]),
                dashboard_layout=random.choice(["default", "compact", "detailed"]),
                notifications_enabled=random.choice([True, False]),
                refresh_interval=random.choice([15, 30, 60])
            )
            db.session.add(preference)
        
        print("✅ Created user preferences")
        
        # Create sample metrics
        print("📊 Creating sample metrics...")
        
        metric_types = ["cpu_usage", "memory_usage", "response_time", "error_rate", "active_users"]
        units = ["%", "%", "ms", "%", "count"]
        
        for user in users:
            for _ in range(random.randint(5, 15)):
                metric = AppMetric(
                    user_id=user.id,
                    metric_type=random.choice(metric_types),
                    value=random.uniform(10, 95),
                    unit=units[metric_types.index(metric_type)],
                    description=f"Sample {metric_type} for {user.username}",
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
                )
                db.session.add(metric)
        
        print("✅ Created sample metrics")
        
        # Create system events
        print("📝 Creating system events...")
        
        event_types = ["info", "warning", "error", "success"]
        severities = ["low", "medium", "high", "critical"]
        sources = ["system", "auth", "sync", "monitoring"]
        
        for _ in range(50):
            event = SystemEvent(
                event_type=random.choice(event_types),
                severity=random.choice(severities),
                message=f"Sample {random.choice(event_types)} event from {random.choice(sources)}",
                source=random.choice(sources),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 168)),
                event_data={
                    "user_id": random.choice(users).id if random.choice([True, False]) else None,
                    "company_id": random.choice(companies).id,
                    "details": "Sample event details"
                }
            )
            db.session.add(event)
        
        print("✅ Created system events")
        
        # Create user activities
        print("👤 Creating user activities...")
        
        activity_types = ["login", "logout", "access", "failed_login", "password_change"]
        
        # Get all SSO applications
        all_apps = SSOApplication.query.all()
        
        for user in users:
            for _ in range(random.randint(10, 30)):
                app = random.choice(all_apps)
                activity = UserActivity(
                    company_id=user.company_id,
                    user_id=user.id,
                    app_id=app.id,
                    activity_type=random.choice(activity_types),
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 168)),
                    ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    location=random.choice(["New York", "London", "Tokyo", "Sydney", "Berlin"]),
                    success=random.choice([True, True, True, False]),  # 75% success
                    failure_reason="Invalid credentials" if random.choice([True, False]) else None,
                    metadata={
                        "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                        "os": random.choice(["Windows", "macOS", "Linux", "iOS", "Android"])
                    }
                )
                db.session.add(activity)
        
        print("✅ Created user activities")
        
        # Commit all changes
        print("💾 Committing all changes to database...")
        db.session.commit()
        
        print("\n🎉 Database initialization completed successfully!")
        print(f"📊 Created {len(companies)} companies")
        print(f"👥 Created {len(users)} users")
        print(f"🔐 Created {len(sso_configs)} SSO configurations")
        print(f"📱 Created {len(all_apps)} SSO applications")
        print(f"📝 Created 50 system events")
        print(f"👤 Created user activities")
        
        # Print sample login credentials
        print("\n🔑 Sample Login Credentials:")
        print("=" * 40)
        for company in companies:
            admin_user = User.query.filter_by(company_id=company.id, is_admin=True).first()
            print(f"Company: {company.name}")
            print(f"  Admin: {admin_user.username} / admin123")
            print(f"  Domain: {company.domain}")
            print()

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
