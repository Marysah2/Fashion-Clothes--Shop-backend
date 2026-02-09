"""
Product catalog routes
Implements CRUD for products, categories, image serving, filtering
"""

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from extensions import db
from models.product import Product, Category
from utils.decorators import admin_required
import os
import uuid

products_bp = Blueprint('products', __name__)

# Configuration for image upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def slugify(text):
    """Convert text to URL-friendly slug"""
    return text.lower().replace(' ', '-').replace('_', '-')

@products_bp.route('/', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Query parameters
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        featured = request.args.get('featured', type=bool)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = Product.query.filter_by(is_active=True)
        
        # Apply filters
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if featured:
            query = query.filter_by(is_featured=True)
        
        # Pagination
        pagination = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Increment view count
        product.view_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    """Create new product (admin only)"""
    data = request.get_json()
    
    required_fields = ['name', 'price', 'category_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    try:
        # Generate slug
        base_slug = slugify(data['name'])
        slug = base_slug
        counter = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1
        
        # Create product
        product = Product(
            name=data['name'],
            slug=slug,
            description=data.get('description'),
            price=data['price'],
            sale_price=data.get('sale_price'),
            sku=data.get('sku') or f'SKU-{uuid.uuid4().hex[:8].upper()}',
            category_id=data['category_id'],
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url'),
            images=','.join(data.get('images', [])) if data.get('images') else None,
            sizes=','.join(data.get('sizes', [])) if data.get('sizes') else None,
            colors=','.join(data.get('colors', [])) if data.get('colors') else None,
            material=data.get('material'),
            is_featured=data.get('is_featured', False)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created',
            'data': product.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """Update product (admin only)"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    try:
        if data.get('name'):
            product.name = data['name']
            product.slug = slugify(data['name'])
        if data.get('description') is not None:
            product.description = data['description']
        if data.get('price'):
            product.price = data['price']
        if data.get('sale_price') is not None:
            product.sale_price = data['sale_price']
        if data.get('category_id'):
            product.category_id = data['category_id']
        if data.get('stock_quantity') is not None:
            product.stock_quantity = data['stock_quantity']
        if data.get('image_url'):
            product.image_url = data['image_url']
        if data.get('sizes'):
            product.sizes = ','.join(data['sizes'])
        if data.get('colors'):
            product.colors = ','.join(data['colors'])
        if data.get('is_active') is not None:
            product.is_active = data['is_active']
        if data.get('is_featured') is not None:
            product.is_featured = data['is_featured']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated',
            'data': product.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """Delete product (admin only)"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== CATEGORY ENDPOINTS =====

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in categories]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """Create new category (admin only)"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Category name required'}), 400
    
    try:
        slug = slugify(data['name'])
        counter = 1
        while Category.query.filter_by(slug=slug).first():
            slug = f'{slugify(data["name"])}-{counter}'
            counter += 1
        
        category = Category(
            name=data['name'],
            slug=slug,
            description=data.get('description'),
            image_url=data.get('image_url'),
            parent_id=data.get('parent_id')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Category created',
            'data': category.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """Update category (admin only)"""
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    try:
        if data.get('name'):
            category.name = data['name']
            category.slug = slugify(data['name'])
        if data.get('description') is not None:
            category.description = data['description']
        if data.get('image_url') is not None:
            category.image_url = data['image_url']
        if data.get('parent_id') is not None:
            category.parent_id = data['parent_id']
        if data.get('is_active') is not None:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Category updated',
            'data': category.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """Delete category (admin only)"""
    category = Category.query.get_or_404(category_id)
    
    try:
        # Move products to another category or delete
        if category.products.count() > 0:
            return jsonify({
                'success': False,
                'message': 'Cannot delete category with products. Move or delete products first.'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Category deleted'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        products = Product.query.filter_by(is_active=True, is_featured=True).limit(10).all()
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
