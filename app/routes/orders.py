from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.order import Order, OrderItem
from app.services.mpesa_service import MpesaService
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def generate_invoice_number():
    return f"INV-{uuid.uuid4().hex[:12].upper()}"

@orders_bp.route('/', methods=['POST'])
def create_order():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    data = request.get_json()

    cart_items = data.get('cart_items') or data.get('items')
    
    if not data or not cart_items or 'shipping_address' not in data:
        return jsonify({'error': 'Missing cart_items/items or shipping_address'}), 400
    shipping_address = data['shipping_address']
    billing_info = data.get('billing_info', shipping_address)
    phone_number = data.get('phone_number', '254703166572')
    payment_method = data.get('payment_method', 'mpesa')

    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total = 0.0
    order_items = []

    for item in cart_items:
        price = 25.99
        total += price * item['quantity']

        order_items.append(OrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            price_at_purchase=price
        ))

    order = Order(
        user_id=user_id,
        total=total,
        shipping_address=shipping_address,
        billing_info=billing_info,
        invoice_number=generate_invoice_number(),
        status='pending'
    )

    db.session.add(order)
    db.session.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.session.add(oi)

    db.session.commit()

    if payment_method == 'mpesa' and phone_number:
        try:
            mpesa = MpesaService()
            mpesa_response = mpesa.stk_push(
                phone_number=phone_number,
                amount=total,
                account_reference=order.invoice_number,
                transaction_desc=f'Payment for Order {order.invoice_number}'
            )
            
            return jsonify({
                'message': 'M-Pesa payment initiated. Check your phone.',
                'order_id': order.id,
                'invoice_number': order.invoice_number,
                'total': float(order.total),
                'status': order.status,
                'mpesa_response': mpesa_response
            }), 201
        except Exception as e:
            return jsonify({
                'message': 'Order created but M-Pesa payment failed',
                'order_id': order.id,
                'invoice_number': order.invoice_number,
                'total': float(order.total),
                'status': order.status,
                'error': str(e)
            }), 201
    
    order.status = 'completed'
    db.session.commit()
    
    return jsonify({
        'message': 'Order placed successfully (simulated payment)',
        'order_id': order.id,
        'invoice_number': order.invoice_number,
        'total': float(order.total),
        'status': order.status,
        'invoice': {
            'invoice_number': order.invoice_number,
            'date': order.created_at.strftime('%Y-%m-%d'),
            'billing_info': order.billing_info,
            'shipping_address': order.shipping_address,
            'items': [{'product_id': oi.product_id, 'quantity': oi.quantity, 'price': float(oi.price_at_purchase)} for oi in order.items],
            'total': float(order.total)
        }
    }), 201

@orders_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    
    result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
    
    if result_code == 0:
        callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
        
        account_ref = None
        for item in callback_metadata:
            if item.get('Name') == 'AccountReference':
                account_ref = item.get('Value')
                break
        
        if account_ref:
            order = Order.query.filter_by(invoice_number=account_ref).first()
            if order:
                order.status = 'completed'
                db.session.commit()
    
    return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200

def get_order(order_id):
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None

    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if user_id and order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'order_id': order.id,
        'invoice_number': order.invoice_number,
        'total': float(order.total),
        'status': order.status,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'shipping_address': order.shipping_address,
        'billing_info': order.billing_info,
        'items': [{
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': float(item.price_at_purchase)
        } for item in order.items]
    }), 200
