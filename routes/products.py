# Product catalog routes
# Kabathi: Implement CRUD for products, categories, image serving, filtering

from flask import Blueprint, request, jsonify, send_from_directory
from models import db
from models.product import Product, Category
from utils.decorators import admin_required
import os

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    category_name = request.args.get('category')
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category_name:
        query = query.join(Category).filter(Category.name == category_name)
    elif category_id:
        query = query.filter_by(category_id=category_id)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.all()
    return jsonify([p.to_dict() for p in products]), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.route('/', methods=['POST'])
@admin_required
def create_product():
    data = request.get_json()
    
    if not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Name and price are required'}), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        stock=data.get('stock', 0),
        image_url=data.get('image_url'),
        category_id=data.get('category_id')
    )
    
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'category_id' in data:
        product.category_id = data['category_id']
    
    db.session.commit()
    return jsonify(product.to_dict()), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200

@products_bp.route('/images/<filename>')
def serve_image(filename):
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    return send_from_directory(images_dir, filename)