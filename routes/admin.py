"""
Admin routes
Implements CRUD for users & roles, product analytics, admin analytics section
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.product import Product
from models.order import Order
from models.cart import Cart, CartItem
from utils.decorators import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ================== USER MANAGEMENT ==================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Get all users (Admin)
    ---
    tags:
      - Admin
    parameters:
      - name: page
        in: query
        schema:
          type: integer
        example: 1
      - name: per_page
        in: query
        schema:
          type: integer
        example: 20
      - name: search
        in: query
        schema:
          type: string
        example: john@example.com
    responses:
      200:
        description: List of users with pagination
      500:
        description: Server error
    """
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
    """
    Get specific user by ID (Admin)
    ---
    tags:
      - Admin
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User object
      404:
        description: User not found
    """
    user = User.query.get_or_404(user_id)
    return jsonify({'success': True, 'data': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """
    Update a user (Admin)
    ---
    tags:
      - Admin
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
              phone:
                type: string
              is_active:
                type: boolean
              is_admin:
                type: boolean
    responses:
      200:
        description: User updated successfully
      500:
        description: Server error
    """
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
        return jsonify({'success': True, 'message': 'User updated', 'data': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Delete a user (Admin)
    ---
    tags:
      - Admin
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User deleted
      400:
        description: Cannot delete own account
      500:
        description: Server error
    """
    user = User.query.get_or_404(user_id)
    try:
        current_user_id = get_jwt_identity()
        if user.id == current_user_id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ===== ROLE MANAGEMENT =====

@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
@admin_required
def get_roles():
    """
    Get all roles (Admin)
    ---
    tags:
      - Role Management
    summary: Retrieve all user roles
    description: Returns a list of all roles in the system
    responses:
      200:
        description: List of roles
        content:
          application/json:
            example:
              success: true
              data:
                - id: 1
                  name: "Admin"
                  description: "Administrator role with full access"
                - id: 2
                  name: "User"
                  description: "Regular user role"
      500:
        description: Internal server error
    """
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
    """
    Create a new role (Admin)
    ---
    tags:
      - Role Management
    summary: Create a new role
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
            properties:
              name:
                type: string
                description: Name of the role
                example: "Manager"
              description:
                type: string
                description: Optional description of the role
                example: "Manager role with limited admin access"
    responses:
      201:
        description: Role created successfully
        content:
          application/json:
            example:
              success: true
              message: "Role created"
              data:
                id: 3
                name: "Manager"
                description: "Manager role with limited admin access"
      400:
        description: Bad request (missing name or duplicate role)
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Role name required'}), 400
    try:
        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'success': False, 'message': 'Role already exists'}), 400
        role = Role(name=data['name'], description=data.get('description'))
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
    """
    Update roles for a user (Admin)
    ---
    tags:
      - Role Management
    summary: Assign or update roles for a specific user
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              roles:
                type: array
                items:
                  type: string
                description: List of role names to assign
                example: ["Admin", "Manager"]
    responses:
      200:
        description: User roles updated successfully
        content:
          application/json:
            example:
              success: true
              message: "User roles updated"
              data:
                id: 5
                name: "John Doe"
                roles:
                  - id: 1
                    name: "Admin"
                  - id: 3
                    name: "Manager"
      500:
        description: Internal server error
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    try:
        role_names = data.get('roles', [])
        user.roles = []  # Clear existing roles
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
    """
    Get all customer orders with optional filtering (Admin)
    ---
    tags:
      - Order Management
    summary: Retrieve orders with optional status filter and pagination
    parameters:
      - name: status
        in: query
        schema:
          type: string
          description: Filter orders by status
          example: "pending"
      - name: page
        in: query
        schema:
          type: integer
          example: 1
      - name: per_page
        in: query
        schema:
          type: integer
          example: 20
    responses:
      200:
        description: List of orders
        content:
          application/json:
            example:
              success: true
              data:
                - id: 10
                  user_id: 5
                  status: "pending"
                  total_amount: 150.5
              pagination:
                page: 1
                per_page: 20
                total: 50
      500:
        description: Internal server error
    """
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
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
    """
    Update status of a specific order (Admin)
    ---
    tags:
      - Order Management
    summary: Change order status
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the order
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - status
            properties:
              status:
                type: string
                description: New status for the order
                enum: ["pending", "processing", "shipped", "delivered", "cancelled"]
                example: "shipped"
    responses:
      200:
        description: Order status updated
        content:
          application/json:
            example:
              success: true
              message: "Order status updated"
              data:
                id: 10
                status: "shipped"
      400:
        description: Invalid status provided
      500:
        description: Internal server error
    """
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
    """
    Get product analytics (Admin)
    ---
    tags:
      - Product Analytics
    summary: Get product statistics for admin dashboard
    description: Returns counts of products, stock levels, most viewed products, featured products, and products by category.
    responses:
      200:
        description: Product analytics data
        content:
          application/json:
            example:
              success: true
              data:
                totalProducts: 120
                activeProducts: 100
                lowStock: 15
                outOfStock: 5
                featuredCount: 10
                mostViewed:
                  - id: 1
                    name: "Product 1"
                    view_count: 150
                  - id: 2
                    name: "Product 2"
                    view_count: 140
                byCategory:
                  - category: "Electronics"
                    count: 50
                  - category: "Clothing"
                    count: 70
      500:
        description: Internal server error
    """
    try:
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        low_stock = Product.query.filter(Product.stock_quantity > 0, Product.stock_quantity <= 10).count()
        out_of_stock = Product.query.filter_by(stock_quantity=0).count()
        most_viewed = Product.query.order_by(Product.view_count.desc()).limit(10).all()
        featured_count = Product.query.filter_by(is_featured=True, is_active=True).count()

        from models.product import Category
        products_by_category = db.session.query(
            Category.name, func.count(Product.id)
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
    """
    Admin dashboard analytics (Admin)
    ---
    tags:
      - Admin Dashboard
    summary: Get overall system metrics for dashboard
    description: Returns user stats, order stats, revenue stats, order status distribution, and recent orders.
    responses:
      200:
        description: Admin dashboard analytics
        content:
          application/json:
            example:
              success: true
              data:
                overview:
                  totalUsers: 150
                  newUsers30d: 10
                  totalOrders: 200
                  orders30d: 20
                  pendingOrders: 5
                  totalRevenue: 5000.0
                  revenue30d: 450.0
                orderStatus:
                  - status: "pending"
                    count: 5
                  - status: "shipped"
                    count: 50
                recentOrders:
                  - id: 101
                    user_id: 1
                    total_amount: 120.0
                    status: "shipped"
      500:
        description: Internal server error
    """
    try:
        today = datetime.utcnow()
        thirty_days_ago = today - timedelta(days=30)

        total_users = User.query.count()
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()

        total_orders = Order.query.count()
        orders_30d = Order.query.filter(Order.created_at >= thirty_days_ago).count()
        pending_orders = Order.query.filter_by(status='pending').count()

        total_revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
        revenue_30d = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(Order.created_at >= thirty_days_ago).scalar() or 0

        status_dist = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
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
    """
    View inventory status (Admin)
    ---
    tags:
      - Inventory Management
    summary: Retrieve product inventory with optional stock filters and pagination
    parameters:
      - name: page
        in: query
        schema:
          type: integer
          example: 1
      - name: per_page
        in: query
        schema:
          type: integer
          example: 50
      - name: stock
        in: query
        schema:
          type: string
          enum: ["out", "low", "normal"]
          description: Filter products by stock status
          example: "low"
    responses:
      200:
        description: Paginated list of products with inventory info
        content:
          application/json:
            example:
              success: true
              data:
                - id: 1
                  name: "Product 1"
                  stock_quantity: 5
                - id: 2
                  name: "Product 2"
                  stock_quantity: 0
              pagination:
                page: 1
                per_page: 50
                total: 120
      500:
        description: Internal server error
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        query = Product.query

        stock_status = request.args.get('stock')
        if stock_status == 'out':
            query = query.filter_by(stock_quantity=0)
        elif stock_status == 'low':
            query = query.filter(Product.stock_quantity > 0, Product.stock_quantity <= 10)
        elif stock_status == 'normal':
            query = query.filter(Product.stock_quantity > 10)

        pagination = query.order_by(Product.stock_quantity.asc()).paginate(page=page, per_page=per_page, error_out=False)
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
    """
    Update product stock quantity (Admin)
    ---
    tags:
      - Inventory Management
    summary: Update stock quantity of a specific product
    parameters:
      - name: product_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the product to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - stock_quantity
            properties:
              stock_quantity:
                type: integer
                description: New stock quantity for the product
                example: 25
    responses:
      200:
        description: Inventory updated successfully
        content:
          application/json:
            example:
              success: true
              message: "Inventory updated"
              data:
                id: 1
                name: "Product 1"
                stock_quantity: 25
      400:
        description: Bad request (missing stock_quantity)
      500:
        description: Internal server error
    """
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