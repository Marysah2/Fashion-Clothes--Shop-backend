from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # guest allowed
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.JSON, nullable=False)
    billing_info = db.Column(db.JSON, nullable=True)
    invoice_number = db.Column(db.String(30), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # No FK constraint for testing
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)