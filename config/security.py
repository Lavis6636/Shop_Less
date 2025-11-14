# security.py - Security configuration and GDPR compliance
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
# Import Flask utilities required by decorators
from flask import session, request, jsonify, flash, redirect, url_for, g

class SecurityConfig:
    """Security configuration and permission management"""
    
    SECRET_KEY = 'shopless-security-key-2024'
    ALGORITHM = 'HS256'
    TOKEN_EXPIRY = 24  # hours
    
    # Role-based permissions
    PERMISSIONS = {
        'Customer': {
            'read': ['products', 'product_details', 'cart', 'own_profile', 'own_orders'],
            'write': ['cart', 'own_profile', 'orders'],
            'delete': ['cart_items', 'own_reviews']
        },
        'Admin': {
            'read': ['*'],
            'write': ['*'],
            'delete': ['*']
        }
    }
    
    @staticmethod
    def generate_token(user_id, username, role):
        """Generate JWT token"""
        # FIX: Ensure all datetime objects are timezone-aware (utcnow is deprecated without tzinfo)
        now = datetime.now(timezone.utc)
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': int((now + timedelta(hours=SecurityConfig.TOKEN_EXPIRY)).timestamp()), # Use int for exp timestamp
            'iat': int(now.timestamp())
        }
        # FIX: Explicitly encode the token as a string (returns bytes, which is standard, but the original comment suggested returning a string)
        # Note: jwt.encode returns bytes, so we should typically decode it to a string for use in headers.
        token_bytes = jwt.encode(payload, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
        return token_bytes.decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            # FIX: The token may be a string, so ensure it's handled correctly by the library
            payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception: # Catch any other decoding issues
            return None
        
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 (Note: In a real app, use scrypt or bcrypt)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def check_permission(role, action, resource):
        """Check if role has permission for action on resource"""
        if role not in SecurityConfig.PERMISSIONS:
            return False
        
        permissions = SecurityConfig.PERMISSIONS[role]
        
        # Check for specific permission or wildcard '*'
        if '*' in permissions.get(action, []) or resource in permissions.get(action, []):
            return True
        
        return False

class DataClassifier:
    """Classify application data into security levels"""
    # ... (No changes needed in this class) ...
    @staticmethod
    def classify_user_data(user_data):
        """Classify user data based on sensitivity"""
        classification = {
            'public': {
                'username', 'role', 'created_at'
            },
            'private': {
                'email', 'last_login'
            },
            'confidential': {
                'password_hash', 'session_token'
            },
            'restricted': {
                'ip_address', 'device_fingerprint', 'payment_methods'
            }
        }
        
        classified = {'public': {}, 'private': {}, 'confidential': {}, 'restricted': {}}
        
        for key, value in user_data.items():
            for level, fields in classification.items():
                if key in fields:
                    classified[level][key] = value
                    break
                
        return classified

class GDPRCompliance:
    """GDPR compliance utilities"""
    # ... (No changes needed in this class) ...
    @staticmethod
    def anonymize_data(data):
        """Anonymize personal data"""
        if 'email' in data:
            data['email'] = '***@***.***'
        if 'ip_address' in data:
            data['ip_address'] = '***.***.***.***'
        if 'device_fingerprint' in data:
            data['device_fingerprint'] = '********'
        return data
    
    @staticmethod
    def get_user_rights():
        """Return GDPR user rights information"""
        return {
            "right_to_access": "Users can access all their personal data",
            "right_to_rectification": "Users can update their personal information",
            "right_to_erasure": "Users can request account deletion",
            "right_to_restrict_processing": "Users can opt-out of data processing",
            "right_to_data_portability": "Users can export their data",
            "right_to_object": "Users can object to specific data uses",
            "data_protection_officer": "dpo@shopless.com"
        }

# Security Decorators (for API routes using JWT)
def jwt_required(f):
    """Decorator to check for a valid JWT token in the Authorization header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # FIX: Check for the header existence before accessing it
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # FIX: Ensure proper Bearer token format check
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]

        if not token:
            return jsonify({'message': 'Token is missing or improperly formatted!'}), 401
        
        try:
            current_user_data = SecurityConfig.verify_token(token)
            if not current_user_data:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token verification error: {str(e)}'}), 401
        
        # Store user info in Flask's g object for easy access in the route
        g.user = current_user_data 
        
        return f(*args, **kwargs)
    return decorated_function

# Security Decorators (for Web/Session routes)
def login_required(f):
    """Decorator for login requirement (using Flask session)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(action, resource):
    """Decorator to check permissions (using Flask session)"""
    def decorator(f):
        @wraps(f)
        @login_required # Ensure user is logged in first
        def decorated_function(*args, **kwargs):
            # FIX: Default role to a safe, low-privilege value
            role = session.get('role', 'Customer') 
            if not SecurityConfig.check_permission(role, action, resource):
                flash('Insufficient permissions.', 'danger')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator for admin-only access (using Flask session)"""
    @wraps(f)
    @login_required # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function