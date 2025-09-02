# 🚀 App Monitor Dashboard

A professional, enterprise-grade SSO monitoring dashboard for Microsoft Entra ID (Azure AD) and other SSO providers. Built with Flask and modern web technologies.

![App Monitor Dashboard](https://img.shields.io/badge/Flask-3.0.0+-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## ✨ Features

- **🔐 SSO Integration**: Seamless integration with Microsoft Entra ID
- **📊 Real-time Monitoring**: Monitor user activity across SSO applications
- **👥 User Management**: Comprehensive user administration and role management
- **🏢 Multi-tenant**: Support for multiple companies and organizations
- **📈 Analytics**: Detailed metrics and reporting on SSO usage
- **🔒 Security**: Role-based access control and audit logging
- **📱 Responsive**: Modern, mobile-friendly interface

## 🏗️ Architecture

- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with proper relationships
- **Authentication**: Flask-Login with secure password hashing
- **Frontend**: Bootstrap 5 with custom CSS and JavaScript
- **Deployment**: Heroku-ready with proper configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Microsoft Entra ID tenant (for SSO integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/app-monitor-dashboard.git
   cd app-monitor-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export FLASK_ENV=development
   export DATABASE_URL=your_database_url
   ```

4. **Initialize database**
   ```bash
   python init_db_enhanced.py
   ```

5. **Run the application**
   ```bash
   python app_new.py
   ```

### Default Credentials

After initialization, you can log in with:
- **Admin**: `admin@techcorp.com` / `admin123`
- **User**: `user1@techcorp.com` / `admin123`

## 🏢 Company Setup

1. **Create Company Profile**: Set up your organization details
2. **Configure Entra ID**: Register application and grant permissions
3. **Test Connection**: Verify integration is working
4. **Sync Applications**: Discover SSO applications automatically
5. **Monitor Activity**: Start tracking user access and usage

## 🔧 Configuration

### Environment Variables

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your_secret_key
```

### Entra ID Setup

1. Register application in Azure Portal
2. Grant required API permissions:
   - `Application.Read.All`
   - `User.Read.All`
   - `AuditLog.Read.All`
   - `Directory.Read.All`
3. Create client secret
4. Configure in the dashboard

## 📁 Project Structure

```
app-monitor/
├── __init__.py              # App factory and configuration
├── models.py                # Database models
├── config.py                # Configuration classes
├── blueprints/              # Route organization
│   ├── auth.py             # Authentication routes
│   ├── main.py             # Main application routes
│   ├── company.py          # Company management
│   └── api.py              # API endpoints
├── templates/               # Jinja2 templates
├── static/                  # CSS, JS, and assets
└── utils/                   # Utility functions
```

## 🚀 Deployment

### Heroku Deployment

1. **Update Procfile**
   ```bash
   cp Procfile.new Procfile
   ```

2. **Update requirements**
   ```bash
   cp requirements_new.txt requirements.txt
   ```

3. **Deploy**
   ```bash
   git push heroku master
   ```

4. **Initialize database**
   ```bash
   heroku run python init_db_enhanced.py
   ```

### Other Platforms

The application is designed to be platform-agnostic and can be deployed to:
- AWS (ECS, Beanstalk)
- Google Cloud Platform
- DigitalOcean
- Docker containers

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📊 API Endpoints

- `GET /api/metrics` - Application metrics
- `GET /api/events` - System events
- `POST /company/sync-entra` - Sync with Entra ID
- `POST /company/test-connection` - Test Entra ID connection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- Microsoft for Entra ID integration
- Bootstrap team for the responsive UI components
- All contributors and users of this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/app-monitor-dashboard/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/app-monitor-dashboard/wiki)
- **Email**: ryan@didurlabs.com

---

**Built with ❤️ by [Ryan Didur](https://github.com/yourusername)**

*Professional SSO monitoring for modern enterprises*
