from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.cart import Cart, CartItem
import uuid

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')

def get_or_create_cart():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None

    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
    else:
        session_id = session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['cart_session_id'] = session_id
        
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
    
    return cart

@cart_bp.route('/', methods=['GET'])
def get_cart():
    cart = get_or_create_cart()
    
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'quantity': item.quantity
    } for item in cart.items]
    
    return jsonify({'cart_id': cart.id, 'items': items}), 200

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'error': 'product_id is required'}), 400
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    if quantity < 1:
        return jsonify({'error': 'quantity must be at least 1'}), 400
    
    cart = get_or_create_cart()
    
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item added to cart',
        'item': {
            'id': cart_item.id,
            'product_id': cart_item.product_id,
            'quantity': cart_item.quantity
        }
    }), 201

@cart_bp.route('/update', methods=['PUT'])
def update_cart_item():
    data = request.get_json()
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'product_id and quantity are required'}), 400
    
    product_id = data['product_id']
    quantity = data['quantity']
    
    if quantity < 1:
        return jsonify({'error': 'quantity must be at least 1'}), 400
    
    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(product_id=product_id, cart_id=cart.id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({
        'message': 'Cart item updated',
        'item': {
            'id': cart_item.id,
            'product_id': cart_item.product_id,
            'quantity': cart_item.quantity
        }
    }), 200

@cart_bp.route('/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(product_id=product_id, cart_id=cart.id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200

@cart_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    cart = get_or_create_cart()
    
    for item in cart.items:
        db.session.delete(item)
    
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared'}), 200
