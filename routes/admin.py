"""
Admin routes for user/role management and analytics
Implements CRUD for users & roles, product analytics, admin analytics section
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Role
from models.product import Product
from models.order import Order
from models.cart import Cart, CartItem
from utils.decorators import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# ===== USER MANAGEMENT =====

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Admin: Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        
        query = User.query
        
        if search:
            query = query.filter(
                (User.email.ilike(f'%{search}%')) | 
                (User.name.ilike(f'%{search}%'))
            )
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Admin: Get specific user"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Admin: Update user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if data.get('name'):
            user.name = data['name']
        if data.get('phone'):
            user.phone = data['phone']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated',
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Admin: Delete user"""
    user = User.query.get_or_404(user_id)
    
    try:
        # Don't allow deleting yourself
        if user.id == get_jwt_identity():
            return jsonify({
                'success': False, 
                'message': 'Cannot delete your own account'
            }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ROLE MANAGEMENT =====

@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
@admin_required
def get_roles():
    """Admin: Get all roles"""
    try:
        roles = Role.query.all()
        return jsonify({
            'success': True,
            'data': [role.to_dict() for role in roles]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/roles', methods=['POST'])
@jwt_required()
@admin_required
def create_role():
    """Admin: Create new role"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Role name required'}), 400
    
    try:
        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'success': False, 'message': 'Role already exists'}), 400
        
        role = Role(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Role created',
            'data': role.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/roles', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_roles(user_id):
    """Admin: Update user roles"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        role_names = data.get('roles', [])
        
        # Clear existing roles
        user.roles = []
        
        # Add new roles
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User roles updated',
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ORDER MANAGEMENT =====

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    """Admin: View all customer orders with filtering"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """Admin: Update order status"""
    data = request.get_json()
    new_status = data.get('status')
    
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Valid: {valid_statuses}'}), 400
    
    order = Order.query.get_or_404(order_id)
    
    try:
        order.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated',
            'data': order.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== PRODUCT ANALYTICS =====

@admin_bp.route('/analytics/products', methods=['GET'])
@jwt_required()
@admin_required
def get_product_analytics():
    """Admin: Get product analytics (counts, most viewed/added-to-cart)"""
    try:
        # Total products
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        
        # Low stock products
        low_stock = Product.query.filter(Product.stock_quantity > 0, Product.stock_quantity <= 10).count()
        out_of_stock = Product.query.filter_by(stock_quantity=0).count()
        
        # Most viewed products
        most_viewed = Product.query.order_by(Product.view_count.desc()).limit(10).all()
        
        # Featured products count
        featured_count = Product.query.filter_by(is_featured=True, is_active=True).count()
        
        # Products by category
        from models.product import Category
        products_by_category = db.session.query(
            Category.name,
            func.count(Product.id)
        ).join(Product).group_by(Category.name).all()
        
        return jsonify({
            'success': True,
            'data': {
                'totalProducts': total_products,
                'activeProducts': active_products,
                'lowStock': low_stock,
                'outOfStock': out_of_stock,
                'featuredCount': featured_count,
                'mostViewed': [p.to_dict() for p in most_viewed],
                'byCategory': [{'category': c, 'count': n} for c, n in products_by_category]
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ADMIN DASHBOARD =====

@admin_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_dashboard():
    """Admin: Analytics dashboard overview"""
    try:
        today = datetime.utcnow()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        
        # User stats
        total_users = User.query.count()
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        # Order stats
        total_orders = Order.query.count()
        orders_30d = Order.query.filter(Order.created_at >= thirty_days_ago).count()
        pending_orders = Order.query.filter_by(status='pending').count()
        
        # Revenue stats
        total_revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
        revenue_30d = db.session.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(Order.created_at >= thirty_days_ago).scalar() or 0
        
        # Order status distribution
        status_dist = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'totalUsers': total_users,
                    'newUsers30d': new_users_30d,
                    'totalOrders': total_orders,
                    'orders30d': orders_30d,
                    'pendingOrders': pending_orders,
                    'totalRevenue': float(total_revenue),
                    'revenue30d': float(revenue_30d)
                },
                'orderStatus': [{'status': s, 'count': c} for s, c in status_dist],
                'recentOrders': [o.to_dict() for o in recent_orders]
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== INVENTORY MANAGEMENT =====

@admin_bp.route('/inventory', methods=['GET'])
@jwt_required()
@admin_required
def get_inventory():
    """Admin: View inventory status"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = Product.query
        
        # Filter by stock status
        stock_status = request.args.get('stock')
        if stock_status == 'out':
            query = query.filter_by(stock_quantity=0)
        elif stock_status == 'low':
            query = query.filter(Product.stock_quantity > 0, Product.stock_quantity <= 10)
        elif stock_status == 'normal':
            query = query.filter(Product.stock_quantity > 10)
        
        pagination = query.order_by(Product.stock_quantity.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/inventory/<int:product_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_inventory(product_id):
    """Admin: Update product stock"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'stock_quantity' not in data:
        return jsonify({'success': False, 'message': 'stock_quantity required'}), 400
    
    try:
        product.stock_quantity = data['stock_quantity']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inventory updated',
            'data': product.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
