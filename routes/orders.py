from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import admin_required
from services.analytics_service import get_user_orders, get_all_orders_admin
from models.order import Order
from extensions import db

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

# ===== CUSTOMER ENDPOINTS =====

@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Customer: Get own order history"""
    user_id = get_jwt_identity()
    try:
        orders = get_user_orders(user_id)
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Customer: Get single order details"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        return jsonify({
            'success': True,
            'data': order.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ADMIN ENDPOINTS =====

@orders_bp.route('/admin/all', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders_admin_route():
    """Admin: View all customer orders with filtering"""
    try:
        # Optional query params: status, start_date, end_date
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        orders = get_all_orders_admin(status, start_date, end_date)
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders],
            'count': len(orders)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/admin/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """Admin: Update order status"""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    order.updated_at = db.func.now()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': order.to_dict()
    }), 200

# ===== ANALYTICS ENDPOINTS =====

@orders_bp.route('/analytics/total', methods=['GET'])
@jwt_required()
@admin_required
def get_total_orders():
    """Admin: Get total orders over time analytics"""
    from services.analytics_service import get_admin_analytics
    
    try:
        analytics = get_admin_analytics()
        return jsonify({
            'success': True,
            'data': {
                'ordersTrend': analytics['ordersTrend'],
                'summary': {
                    'totalOrders': analytics['summary']['totalOrders']
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/analytics/revenue', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_analytics():
    """Admin: Get revenue simulation analytics"""
    from services.analytics_service import get_admin_analytics
    
    try:
        analytics = get_admin_analytics()
        return jsonify({
            'success': True,
            'data': {
                'revenueTrend': analytics['revenueTrend'],
                'summary': {
                    'totalRevenue': analytics['summary']['totalRevenue'],
                    'avgOrderValue': analytics['summary']['avgOrderValue']
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/analytics/categories', methods=['GET'])
@jwt_required()
@admin_required
def get_category_analytics():
    """Admin: Get category-level order statistics"""
    from services.analytics_service import get_admin_analytics
    
    try:
        analytics = get_admin_analytics()
        return jsonify({
            'success': True,
            'data': {
                'categoryStatistics': analytics['categoryStatistics']
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/admin/analytics', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_analytics_endpoint():
    """Admin: Get comprehensive analytics dashboard"""
    from services.analytics_service import get_admin_analytics
    
    try:
        analytics = get_admin_analytics()
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
