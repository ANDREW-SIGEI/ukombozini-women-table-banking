from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from app.models import User, GroupMembership
from app.utils.errors import AuthorizationError

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            raise AuthorizationError('Admin privileges required')
        return f(*args, **kwargs)
    return decorated_function

def field_officer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'field_officer':
            raise AuthorizationError('Field officer privileges required')
        return f(*args, **kwargs)
    return decorated_function

def group_role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(group_id, *args, **kwargs):
            if not current_user.is_authenticated:
                raise AuthorizationError('Authentication required')
            
            membership = GroupMembership.query.filter_by(
                user_id=current_user.id,
                group_id=group_id
            ).first()
            
            if not membership or membership.role not in roles:
                raise AuthorizationError(f'One of these roles required: {", ".join(roles)}')
            
            return f(group_id, *args, **kwargs)
        return decorated_function
    return decorator

def verify_token(token):
    """Verify an authentication token"""
    user = User.verify_reset_password_token(token)
    if not user:
        raise AuthorizationError('Invalid or expired token')
    return user

def get_token():
    """Extract token from Authorization header"""
    auth = request.headers.get('Authorization')
    if not auth:
        raise AuthorizationError('Authorization header is missing')
    
    try:
        token_type, token = auth.split()
        if token_type.lower() != 'bearer':
            raise AuthorizationError('Invalid token type')
        return token
    except ValueError:
        raise AuthorizationError('Invalid Authorization header format')

def check_permission(user_id=None, group_id=None):
    """Check if current user has permission to access a resource"""
    if current_user.role == 'admin':
        return True
    
    if user_id and current_user.id != user_id:
        return False
    
    if group_id:
        membership = GroupMembership.query.filter_by(
            user_id=current_user.id,
            group_id=group_id
        ).first()
        if not membership or membership.role not in ['chairperson', 'secretary', 'treasurer']:
            return False
    
    return True 