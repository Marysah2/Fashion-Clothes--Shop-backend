"""
Cart and Checkout models
Implements cart items, checkout, order creation, payment simulation
"""

from datetime import datetime
from . import db

class Cart(db.Model):
    """Shopping cart model"""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_total(self):
        """Calculate total price of cart items"""
        return sum(item.quantity * item.unit_price for item in self.items)
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    def clear(self):
        """Remove all items from cart"""
        self.items.delete()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total': float(self.get_total()),
            'item_count': self.get_item_count()
        }
    
    def __repr__(self):
        return f'<Cart {self.user_id}>'

class CartItem(db.Model):
    """Individual cart item"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    size = db.Column(db.String(20))
    color = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    product = db.relationship('Product')
    
    def get_total(self):
        """Calculate total for this item"""
        return self.quantity * self.unit_price
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_image': self.product_image,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total': float(self.get_total()),
            'size': self.size,
            'color': self.color
        }
    
    def __repr__(self):
        return f'<CartItem {self.product_name} x{self.quantity}>'

class Invoice(db.Model):
    """Invoice model for orders"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax = db.Column(db.Numeric(10, 2), default=0)
    shipping_fee = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    pdf_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='invoice')
    user = db.relationship('User')
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.invoice_number = f'INV-{timestamp}-{self.id}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'subtotal': float(self.subtotal),
            'tax': float(self.tax),
            'shipping_fee': float(self.shipping_fee),
            'total': float(self.total),
            'pdf_url': self.pdf_url,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
