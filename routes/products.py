"""
Product catalog routes
Implements CRUD for products, categories, image serving, filtering
"""

from flask import Blueprint, request, jsonify, send_from_directory
from extensions import db
from models.product import Product, Category
from utils.decorators import admin_required
import os

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
    """
    List all products with optional filters
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: category
        type: string
        required: false
        description: Filter by category name
        example: Electronics
      - in: query
        name: category_id
        type: integer
        required: false
        description: Filter by category ID
        example: 2
      - in: query
        name: min_price
        type: number
        format: float
        required: false
        example: 10.0
      - in: query
        name: max_price
        type: number
        format: float
        required: false
        example: 100.0
      - in: query
        name: search
        type: string
        required: false
        description: Search term in product name
        example: iPhone
    responses:
      200:
        description: List of products
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: iPhone 14
              description:
                type: string
                example: Latest Apple smartphone
              price:
                type: number
                format: float
                example: 999.99
              stock:
                type: integer
                example: 50
              image_url:
                type: string
                example: "/static/images/iphone14.png"
              category_id:
                type: integer
                example: 2
    """
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
    """
    Get single product details
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Product details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: iPhone 14
            description:
              type: string
              example: Latest Apple smartphone
            price:
              type: number
              format: float
              example: 999.99
            stock:
              type: integer
              example: 50
            image_url:
              type: string
              example: "/static/images/iphone14.png"
            category_id:
              type: integer
              example: 2
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route('/', methods=['POST'])
@admin_required
def create_product():
    """
    Create a new product (Admin only)
    ---
    tags:
      - Products
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - price
            properties:
              name:
                type: string
                example: iPhone 14
              description:
                type: string
                example: Latest Apple smartphone
              price:
                type: number
                format: float
                example: 999.99
              stock:
                type: integer
                example: 50
              image_url:
                type: string
                example: "/static/images/iphone14.png"
              category_id:
                type: integer
                example: 2
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
      400:
        description: Invalid input
    """
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
    """
    Update product details (Admin only)
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: iPhone 14 Pro
              description:
                type: string
                example: Updated Apple smartphone
              price:
                type: number
                format: float
                example: 1099.99
              stock:
                type: integer
                example: 40
              image_url:
                type: string
                example: "/static/images/iphone14pro.png"
              category_id:
                type: integer
                example: 2
    responses:
      200:
        description: Product updated successfully
        schema:
          type: object
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    for key in ['name', 'description', 'price', 'stock', 'image_url', 'category_id']:
        if key in data:
            setattr(product, key, data[key])
    db.session.commit()
    return jsonify(product.to_dict()), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    Delete a product (Admin only)
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Product deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Product deleted
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    List all categories
    ---
    tags:
      - Products
    responses:
      200:
        description: List of categories
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: Electronics
    """
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200


@products_bp.route('/images/<filename>')
def serve_image(filename):
    """
    Serve product images
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        example: iphone14.png
    responses:
      200:
        description: Image file served
      404:
        description: File not found
    """
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    return send_from_directory(images_dir, filename)
