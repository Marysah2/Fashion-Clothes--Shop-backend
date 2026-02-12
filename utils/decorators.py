"""
Utility decorators for authentication and authorization
Global error handling and logging utilities
"""

from functools import wraps
from flask import jsonify

from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

def admin_required(fn):
    """
    Decorator to restrict access to admin users only.
    Verifies JWT token and checks if user has admin role.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        from models.user import User
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def login_required(fn):
    """
    Decorator to require authentication.
    Verifies JWT token is present and valid.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        from models.user import User
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        return fn(*args, **kwargs)
    return wrapper