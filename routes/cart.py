"""
Cart and checkout routes
Implements cart operations, checkout flow, payment simulation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.cart import Cart, CartItem
from models.product import Product
from models.order import Order, OrderItem
from models.user import User

cart_bp = Blueprint('cart', __name__)

def get_or_create_cart(user_id):
    """Get existing cart or create new one for user"""
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """Get current user's cart"""
    try:
        user_id = get_jwt_identity()
        cart = get_or_create_cart(user_id)
        
        return jsonify({
            'success': True,
            'data': cart.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    
    required_fields = ['product_id', 'quantity']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    try:
        user_id = get_jwt_identity()
        cart = get_or_create_cart(user_id)
        
        # Get product
        product = Product.query.get_or_404(data['product_id'])
        
        # Check if product is active
        if not product.is_active:
            return jsonify({'success': False, 'message': 'Product not available'}), 400
        
        # Check stock
        if product.stock_quantity < data['quantity']:
            return jsonify({
                'success': False, 
                'message': f'Only {product.stock_quantity} items available'
            }), 400
        
        # Check if item already in cart
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id, 
            product_id=product.id,
            size=data.get('size'),
            color=data.get('color')
        ).first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + data['quantity']
            if new_quantity > product.stock_quantity:
                return jsonify({
                    'success': False,
                    'message': f'Cannot add more. Max available: {product.stock_quantity}'
                }), 400
            existing_item.quantity = new_quantity
            existing_item.unit_price = float(product.current_price)
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.image_url,
                quantity=data['quantity'],
                unit_price=float(product.current_price),
                size=data.get('size'),
                color=data.get('color')
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'data': cart.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart_item():
    """Update cart item quantity"""
    data = request.get_json()
    
    if not data.get('item_id') or data.get('quantity') is None:
        return jsonify({'success': False, 'message': 'item_id and quantity required'}), 400
    
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        
        cart_item = CartItem.query.filter_by(
            id=data['item_id'], 
            cart_id=cart.id
        ).first_or_404()
        
        # Check stock
        product = Product.query.get(cart_item.product_id)
        if product and data['quantity'] > product.stock_quantity:
            return jsonify({
                'success': False,
                'message': f'Only {product.stock_quantity} items available'
            }), 400
        
        if data['quantity'] <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = data['quantity']
            cart_item.unit_price = float(product.current_price) if product else cart_item.unit_price
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'data': cart.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        
        cart_item = CartItem.query.filter_by(
            id=item_id, 
            cart_id=cart.id
        ).first_or_404()
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'data': cart.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from cart"""
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared',
            'data': cart.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Process checkout and create order"""
    data = request.get_json()
    
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        
        if cart.items.count() == 0:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Validate shipping address
        if not data.get('shipping_address'):
            return jsonify({'success': False, 'message': 'Shipping address required'}), 400
        
        # Prepare cart items for order
        cart_items_data = []
        for item in cart.items:
            product = Product.query.get(item.product_id)
            if product:
                # Update stock
                product.stock_quantity -= item.quantity
                
                cart_items_data.append({
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'product_image': item.product_image,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'category_name': product.category.name if product.category else 'Uncategorized'
                })
        
        # Create order
        order = Order.create_from_cart(
            user_id=user_id,
            cart_items=cart_items_data,
            shipping_address=data['shipping_address'],
            payment_method=data.get('payment_method', 'online')
        )
        
        db.session.add(order)
        
        # Generate invoice number after order is added
        db.session.flush()
        order.generate_invoice_number()
        
        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'data': {
                'order': order.to_dict()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/payment/simulate', methods=['POST'])
@jwt_required()
def simulate_payment():
    """Simulate payment processing"""
    data = request.get_json()
    
    try:
        user_id = get_jwt_identity()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'success': False, 'message': 'Order ID required'}), 400
        
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        # Simulate payment (always succeeds in demo)
        order.payment_status = 'paid'
        order.status = 'processing'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment simulated successfully',
            'data': {
                'order': order.to_dict(),
                'payment': {
                    'status': 'success',
                    'transaction_id': f'TXN-{order.id}-{order.created_at.strftime("%Y%m%d%H%M%S")}'
                }
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cart_bp.route('/count', methods=['GET'])
@jwt_required()
def get_cart_count():
    """Get total item count in cart"""
    try:
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            return jsonify({
                'success': True,
                'data': {'count': 0}
            }), 200
        
        return jsonify({
            'success': True,
            'data': {'count': cart.get_item_count()}
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
