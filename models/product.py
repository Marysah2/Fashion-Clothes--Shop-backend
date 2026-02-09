"""
Product and Category models for catalog management
Implements product/category models, CRUD endpoints, image serving, filtering
"""

from datetime import datetime
from extensions import db

class Category(db.Model):
    """Category model for organizing products"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for subcategories
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image_url': self.image_url,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }

class Product(db.Model):
    """Product model for catalog items"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2))
    sku = db.Column(db.String(50), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    images = db.Column(db.Text)  # JSON array of additional image URLs
    sizes = db.Column(db.Text)  # JSON array of available sizes
    colors = db.Column(db.Text)  # JSON array of available colors
    material = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': float(self.price),
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'sku': self.sku,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'images': self.images.split(',') if self.images else [],
            'sizes': self.sizes.split(',') if self.sizes else [],
            'colors': self.colors.split(',') if self.colors else [],
            'material': self.material,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'view_count': self.view_count
        }
    
    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price
