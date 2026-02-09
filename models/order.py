"""
Order and OrderItem models
Manages customer orders and order line items
"""

from datetime import datetime
from extensions import db
import json

class OrderItem(db.Model):
    """Individual order line item"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    category_name = db.Column(db.String(100))  # For analytics
    
    # Relationships
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product')
    
    def to_dict(self):
        return {
            'id': self.id,
            'productId': self.product_id,
            'name': self.product_name,
            'image': self.product_image,
            'quantity': self.quantity,
            'price': float(self.unit_price),
            'total': float(self.total_price),
            'category_name': self.category_name
        }
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'

class Order(db.Model):
    """Customer order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    invoice_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, shipped, delivered, cancelled
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2))
    shipping_fee = db.Column(db.Numeric(10, 2), default=0.00)
    items = db.Column(db.Text, nullable=False)  # JSON string for SQLite compatibility
    shipping_address = db.Column(db.Text)  # JSON string for SQLite compatibility
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    # Property to access items as dict
    @property
    def items_dict(self):
        """Return items as parsed JSON dict."""
        if isinstance(self.items, str):
            return json.loads(self.items)
        return self.items
    
    @items_dict.setter
    def items_dict(self, value):
        """Set items from dict, stored as JSON string."""
        self.items = json.dumps(value) if value else '[]'
    
    # Property to access shipping_address as dict
    @property
    def address_dict(self):
        """Return shipping_address as parsed JSON dict."""
        if isinstance(self.shipping_address, str):
            return json.loads(self.shipping_address) if self.shipping_address else None
        return self.shipping_address
    
    @address_dict.setter
    def address_dict(self, value):
        """Set shipping_address from dict, stored as JSON string."""
        self.shipping_address = json.dumps(value) if value else None
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.invoice_number = f'INV-{timestamp}-{self.id}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customerId': self.user_id,
            'items': self.items_dict if isinstance(self.items, str) else self.items,
            'totalAmount': float(self.total_amount),
            'subtotal': float(self.subtotal) if self.subtotal else float(self.total_amount),
            'shippingFee': float(self.shipping_fee),
            'status': self.status,
            'paymentStatus': self.payment_status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'customer': {
                'name': self.user.name if self.user else 'Unknown',
                'email': self.user.email if self.user else 'unknown@example.com',
                'phone': self.user.phone if hasattr(self.user, 'phone') and self.user.phone else 'N/A'
            },
            'shippingAddress': self.address_dict
        }
    
    def calculate_totals(self):
        """Calculate subtotal and total_amount from order_items"""
        if self.order_items:
            self.subtotal = sum(item.total_price for item in self.order_items)
            self.total_amount = self.subtotal + (self.shipping_fee or 0)
    
    @staticmethod
    def create_from_cart(user_id, cart_items, shipping_address=None, payment_method=None):
        """
        Create an order from cart items
        cart_items should be a list of dictionaries with:
        - product_id
        - product_name
        - quantity
        - unit_price
        - category_name
        """
        # Calculate totals
        subtotal = sum(item['unit_price'] * item['quantity'] for item in cart_items)
        shipping_fee = 0.00
        total_amount = subtotal + shipping_fee
        
        # Prepare items JSON
        items_json = json.dumps([{
            'product_id': item['product_id'],
            'name': item['product_name'],
            'price': float(item['unit_price']),
            'quantity': item['quantity'],
            'category_name': item.get('category_name', 'Uncategorized'),
            'image': item.get('product_image', '')
        } for item in cart_items])
        
        # Prepare shipping address JSON
        shipping_address_json = json.dumps(shipping_address) if shipping_address else None
        
        # Create order
        order = Order(
            user_id=user_id,
            status='pending',
            total_amount=total_amount,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            items=items_json,
            shipping_address=shipping_address_json,
            payment_method=payment_method,
            payment_status='pending'
        )
        
        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_image=item.get('product_image', ''),
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['unit_price'] * item['quantity'],
                category_name=item.get('category_name', 'Uncategorized')
            )
            order.order_items.append(order_item)
        
        return order
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'
