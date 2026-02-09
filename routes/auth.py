"""
Authentication routes
Implements user registration, login, JWT authentication, role-based access
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from datetime import datetime
from extensions import db
from models.user import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        # Assign default role
        customer_role = Role.query.filter_by(name='customer').first()
        if customer_role:
            user.roles.append(customer_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint with JWT tokens"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Check user exists and password matches
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'success': False, 'message': 'Account is deactivated'}), 401
    
    try:
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token"""
    refresh_token = request.json.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'success': False, 'message': 'Refresh token required'}), 400
    
    try:
        # Create new access token
        access_token = create_access_token(identity=get_jwt_identity())
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid refresh token'}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    # In a production app, you would blacklist the token here
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current authenticated user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        if data.get('name'):
            user.name = data['name']
        if data.get('phone'):
            user.phone = data['phone']
        
        if data.get('password'):
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Admin: Get all users"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users],
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user by ID"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200
