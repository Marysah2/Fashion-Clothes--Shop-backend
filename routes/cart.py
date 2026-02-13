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

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


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
    """
    Get current user's cart
    ---
    tags:
      - Cart
    responses:
      200:
        description: Current cart details
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = get_or_create_cart(user_id)
        return jsonify({'success': True, 'data': cart.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """
    Add item to cart
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: item
        required: true
        schema:
          type: object
          required:
            - product_id
            - quantity
          properties:
            product_id:
              type: integer
              example: 1
            quantity:
              type: integer
              example: 2
            size:
              type: string
              example: M
            color:
              type: string
              example: red
    responses:
      200:
        description: Item added successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Item added to cart"
            data:
              type: object
      400:
        description: Invalid request or stock issues
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """
    data = request.get_json()
    required_fields = ['product_id', 'quantity']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = get_or_create_cart(user_id)
        product = Product.query.get_or_404(data['product_id'])

        if product.stock < data['quantity']:
            return jsonify({
                'success': False,
                'message': f'Only {product.stock} items available'
            }), 400

        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=product.id,
            size=data.get('size'),
            color=data.get('color')
        ).first()
        if existing_item:
            new_quantity = existing_item.quantity + data['quantity']
            if new_quantity > product.stock:
                return jsonify({
                    'success': False,
                    'message': f'Cannot add more. Max available: {product.stock}'
                }), 400
            existing_item.quantity = new_quantity
            existing_item.unit_price = float(product.price)
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.image_url,
                quantity=data['quantity'],
                unit_price=float(product.price),
                size=data.get('size'),
                color=data.get('color')
            )
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Item added to cart', 'data': cart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart_item():
    """
    Update cart item quantity
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: item
        required: true
        schema:
          type: object
          required:
            - item_id
            - quantity
          properties:
            item_id:
              type: integer
              example: 1
            quantity:
              type: integer
              example: 3
    responses:
      200:
        description: Cart updated
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Cart updated"
            data:
              type: object
      400:
        description: Invalid request or stock issues
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """
    data = request.get_json()
    if not data.get('item_id') or data.get('quantity') is None:
        return jsonify({'success': False, 'message': 'item_id and quantity required'}), 400
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        cart_item = CartItem.query.filter_by(id=data['item_id'], cart_id=cart.id).first_or_404()
        product = Product.query.get(cart_item.product_id)
        if product and data['quantity'] > product.stock:
            return jsonify({
                'success': False,
                'message': f'Only {product.stock} items available'
            }), 400

        if data['quantity'] <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = data['quantity']
            cart_item.unit_price = float(product.price) if product else cart_item.unit_price

        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart updated', 'data': cart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """
    Remove item from cart
    ---
    tags:
      - Cart
    parameters:
      - in: path
        name: item_id
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Item removed
      500:
        description: Server error
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart', 'data': cart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """
    Clear all items from cart
    ---
    tags:
      - Cart
    responses:
      200:
        description: Cart cleared
      500:
        description: Server error
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart cleared', 'data': cart.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """
    Process checkout and create order
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: order
        required: true
        schema:
          type: object
          required:
            - shipping_address
          properties:
            shipping_address:
              type: string
              example: "123 Main Street, Nairobi"
            payment_method:
              type: string
              example: "online"
    responses:
      201:
        description: Order created successfully
      400:
        description: Invalid request
      500:
        description: Server error
    """
    # (same code as your original checkout function)
    data = request.get_json()
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = Cart.query.filter_by(user_id=user_id).first_or_404()
        if cart.items.count() == 0:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 422
        if not data.get('shipping_address'):
            return jsonify({'success': False, 'message': 'Shipping address required'}), 422

        cart_items_data = []
        for item in cart.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock -= item.quantity
                cart_items_data.append({
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'product_image': item.product_image,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'category_name': product.category.name if product.category else 'Uncategorized'
                })

        order = Order.create_from_cart(
            user_id=user_id,
            cart_items=cart_items_data,
            shipping_address=data['shipping_address'],
            payment_method=data.get('payment_method', 'online')
        )
        db.session.add(order)
        db.session.flush()
        order.generate_invoice_number()
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Order created successfully', 'data': {'order': order.to_dict()}}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Checkout error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@cart_bp.route('/payment/simulate', methods=['POST'])
@jwt_required()
def simulate_payment():
    """
    Simulate payment processing
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: payment
        required: true
        schema:
          type: object
          required:
            - order_id
          properties:
            order_id:
              type: integer
              example: 1
    responses:
      200:
        description: Payment simulated successfully
      400:
        description: Invalid request
      500:
        description: Server error
    """
    data = request.get_json()
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        order_id = data.get('order_id')
        if not order_id:
            return jsonify({'success': False, 'message': 'Order ID required'}), 400
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
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
    """
    Get total item count in cart
    ---
    tags:
      - Cart
    responses:
      200:
        description: Returns cart item count
      500:
        description: Server error
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['id'] if isinstance(identity, dict) else identity
        cart = Cart.query.filter_by(user_id=user_id).first()
        count = cart.get_item_count() if cart else 0
        return jsonify({'success': True, 'data': {'count': count}}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500