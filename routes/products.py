# Product catalog routes
# Kabathi: Implement CRUD for products, categories, image serving, filtering

from flask import Blueprint, request, jsonify

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    # TODO: Implement product listing with filtering/sorting
    pass

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # TODO: Implement single product retrieval
    pass

@products_bp.route('/', methods=['POST'])
def create_product():
    # TODO: Implement product creation (admin only)
    pass

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    # TODO: Implement product update (admin only)
    pass

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    # TODO: Implement product deletion (admin only)
    pass

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    # TODO: Implement category listing
    pass

@products_bp.route('/images/<filename>')
def serve_image(filename):
    # TODO: Implement image serving
    pass