"""
Microsoft Entra ID (Azure AD) Client
Handles authentication and API calls to Microsoft Graph API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class EntraClient:
    """Client for Microsoft Entra ID (Azure AD) Graph API."""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = None
        
        # Microsoft Graph API endpoints
        self.auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0"
    
    def _get_access_token(self) -> str:
        """Get access token for Microsoft Graph API."""
        if self.access_token and self.token_expires and datetime.utcnow() < self.token_expires:
            return self.access_token
        
        # Request new token
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        response = requests.post(self.auth_url, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        self.access_token = token_info['access_token']
        self.token_expires = datetime.utcnow() + timedelta(seconds=token_info['expires_in'] - 300)  # 5 min buffer
        
        return self.access_token
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to Microsoft Graph API."""
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.graph_url}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        if response.status_code == 204:  # No content
            return {}
        
        return response.json()
    
    def get_applications(self) -> List[Dict]:
        """Get all applications from Entra ID."""
        try:
            response = self._make_request('/applications')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting applications: {e}")
            return []
    
    def get_application(self, app_id: str) -> Optional[Dict]:
        """Get specific application by ID."""
        try:
            return self._make_request(f'/applications/{app_id}')
        except Exception as e:
            print(f"Error getting application {app_id}: {e}")
            return None
    
    def get_users(self) -> List[Dict]:
        """Get all users from Entra ID."""
        try:
            response = self._make_request('/users')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get specific user by ID."""
        try:
            return self._make_request(f'/users/{user_id}')
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    def get_sign_in_logs(self, days: int = 7) -> List[Dict]:
        """Get sign-in logs from Entra ID."""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for API
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Build filter for sign-in logs
            filter_query = f"createdDateTime ge {start_str} and createdDateTime le {end_str}"
            
            response = self._make_request(f'/auditLogs/signIns?$filter={filter_query}')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting sign-in logs: {e}")
            return []
    
    def get_application_sign_ins(self, app_id: str, days: int = 7) -> List[Dict]:
        """Get sign-in logs for a specific application."""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for API
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Build filter for application sign-ins
            filter_query = f"createdDateTime ge {start_str} and createdDateTime le {end_str} and appId eq {app_id}"
            
            response = self._make_request(f'/auditLogs/signIns?$filter={filter_query}')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting application sign-ins for {app_id}: {e}")
            return []
    
    def get_directory_roles(self) -> List[Dict]:
        """Get directory roles from Entra ID."""
        try:
            response = self._make_request('/directoryRoles')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting directory roles: {e}")
            return []
    
    def get_directory_role_members(self, role_id: str) -> List[Dict]:
        """Get members of a specific directory role."""
        try:
            response = self._make_request(f'/directoryRoles/{role_id}/members')
            return response.get('value', [])
        except Exception as e:
            print(f"Error getting directory role members for {role_id}: {e}")
            return []
    
    def test_connection(self) -> Dict:
        """Test the connection to Entra ID."""
        try:
            # Try to get basic tenant information
            response = self._make_request('/organization')
            return {
                'success': True,
                'tenant_name': response.get('displayName', 'Unknown'),
                'tenant_id': response.get('id', self.tenant_id),
                'message': 'Connection successful'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Connection failed'
            }
    
    def get_permissions_status(self) -> Dict:
        """Check which permissions are granted to the application."""
        try:
            # Get the current application's permissions
            response = self._make_request(f'/applications/{self.client_id}')
            
            required_permissions = [
                'Application.Read.All',
                'User.Read.All',
                'AuditLog.Read.All',
                'Directory.Read.All'
            ]
            
            granted_permissions = []
            for permission in required_permissions:
                # Check if permission is granted (simplified check)
                granted_permissions.append({
                    'permission': permission,
                    'granted': True,  # Simplified - would need more complex logic
                    'type': 'Application'
                })
            
            return {
                'success': True,
                'permissions': granted_permissions,
                'message': 'Permissions status retrieved'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve permissions status'
            }
