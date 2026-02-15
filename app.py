from flask import Flask
import os
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from extensions import db
from models.tokenblacklist import TokenBlacklist
# Import all models to ensure relationships are properly configured
from models.user import User
from models.product import Product, Category
from models.cart import Cart, CartItem, Invoice
from models.order import Order, OrderItem

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    @app.route('/')
    def home():
        return {
            "message": "Fashion Clothes Shop API",
            "status": "running",
            "documentation": "/swagger/",
            "endpoints": {
                "auth": "/api/auth",
                "products": "/api/products",
                "cart": "/api/cart",
                "orders": "/api/orders",
                "admin": "/api/admin"
            }
        }
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {"status": "healthy", "message": "Backend is running"}, 200
    
    @app.route('/api/seed-database', methods=['POST'])
    def seed_database():
        """Seed database with initial data - call once after deployment"""
        try:
            from models.product import Product, Category
            from models.user import User
            
            # Create admin user
            admin = User.query.filter_by(email='admin@shop.com').first()
            if not admin:
                admin = User(email='admin@shop.com', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
            
            # Create categories
            categories_data = [
                {'name': 'Men', 'description': 'Fashion for men'},
                {'name': 'Women', 'description': 'Fashion for women'},
                {'name': 'Children', 'description': 'Fashion for children'},
                {'name': 'Accessories', 'description': 'Fashion accessories'}
            ]
            
            for cat_data in categories_data:
                if not Category.query.filter_by(name=cat_data['name']).first():
                    category = Category(**cat_data)
                    db.session.add(category)
            
            db.session.commit()
            
            # Create products
            men_cat = Category.query.filter_by(name='Men').first()
            women_cat = Category.query.filter_by(name='Women').first()
            children_cat = Category.query.filter_by(name='Children').first()
            accessories_cat = Category.query.filter_by(name='Accessories').first()
            
            products_data = [
                # Men
                {'name': 'Nairobi Skyline T-Shirt', 'description': 'Cotton tee with Nairobi skyline print', 'price': 1500, 'stock': 50, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'},
                {'name': 'Slim Fit Denim Jeans', 'description': 'Modern slim fit blue jeans', 'price': 3500, 'stock': 30, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'},
                {'name': 'Leather Biker Jacket', 'description': 'Premium leather jacket', 'price': 12000, 'stock': 10, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400'},
                {'name': 'White Sneakers', 'description': 'Classic white canvas sneakers', 'price': 3500, 'stock': 40, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400'},
                {'name': 'Classic Black Jeans', 'description': 'Versatile black denim', 'price': 3200, 'stock': 35, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400'},
                {'name': 'Bomber Jacket', 'description': 'Stylish bomber jacket', 'price': 5500, 'stock': 15, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400'},
                {'name': 'Casual Polo Shirt', 'description': 'Comfortable polo shirt', 'price': 2200, 'stock': 45, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400'},
                {'name': 'Chino Pants', 'description': 'Smart casual chino pants', 'price': 3800, 'stock': 28, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400'},
                {'name': 'Formal Dress Shirt', 'description': 'Classic white dress shirt', 'price': 2800, 'stock': 32, 'category_id': men_cat.id, 'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400'},
                # Women
                {'name': 'Ankara Print Dress', 'description': 'Vibrant African print dress', 'price': 4500, 'stock': 20, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400'},
                {'name': 'Kitenge Maxi Dress', 'description': 'Traditional Kitenge fabric maxi dress', 'price': 5500, 'stock': 15, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400'},
                {'name': 'Evening Cocktail Dress', 'description': 'Elegant evening wear', 'price': 6500, 'stock': 12, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400'},
                {'name': 'Denim Jacket', 'description': 'Classic blue denim jacket', 'price': 4500, 'stock': 18, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400'},
                {'name': 'Leather Boots', 'description': 'Brown leather ankle boots', 'price': 6500, 'stock': 20, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400'},
                {'name': 'Floral Blouse', 'description': 'Elegant floral print blouse', 'price': 2800, 'stock': 35, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1564257577-1f5b3e7c6c3d?w=400'},
                {'name': 'High Waist Skirt', 'description': 'Stylish high waist skirt', 'price': 3200, 'stock': 25, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400'},
                {'name': 'Cardigan Sweater', 'description': 'Cozy knit cardigan', 'price': 3800, 'stock': 22, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400'},
                {'name': 'Silk Scarf', 'description': 'Luxury silk scarf', 'price': 1800, 'stock': 40, 'category_id': women_cat.id, 'image_url': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400'},
                # Children
                {'name': 'Maasai Pattern Tee', 'description': 'Traditional Maasai pattern design', 'price': 1800, 'stock': 40, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400'},
                {'name': 'Safari Print T-Shirt', 'description': 'Wildlife safari themed tee', 'price': 1600, 'stock': 45, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400'},
                {'name': 'Kids Denim Jeans', 'description': 'Comfortable denim for kids', 'price': 2500, 'stock': 35, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1475178626620-a4d074967452?w=400'},
                {'name': 'Running Shoes', 'description': 'Comfortable sports shoes', 'price': 3000, 'stock': 30, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'},
                {'name': 'Hoodie Sweatshirt', 'description': 'Warm and cozy hoodie', 'price': 2200, 'stock': 38, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400'},
                {'name': 'Cartoon Print Dress', 'description': 'Fun cartoon character dress', 'price': 2000, 'stock': 28, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=400'},
                {'name': 'Sports Shorts', 'description': 'Active wear shorts', 'price': 1400, 'stock': 42, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=400'},
                {'name': 'Winter Jacket', 'description': 'Warm winter jacket for kids', 'price': 4200, 'stock': 20, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=400'},
                {'name': 'School Backpack', 'description': 'Durable school backpack', 'price': 2800, 'stock': 25, 'category_id': children_cat.id, 'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'},
                # Accessories
                {'name': 'Beaded Maasai Necklace', 'description': 'Handcrafted Maasai beaded necklace', 'price': 1200, 'stock': 50, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=400'},
                {'name': 'Leather Belt', 'description': 'Genuine leather belt', 'price': 1500, 'stock': 35, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=400'},
                {'name': 'Sunglasses', 'description': 'UV protection sunglasses', 'price': 2000, 'stock': 45, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400'},
                {'name': 'Leather Wallet', 'description': 'Premium leather wallet', 'price': 1800, 'stock': 40, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=400'},
                {'name': 'Wrist Watch', 'description': 'Stylish analog watch', 'price': 5500, 'stock': 15, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=400'},
                {'name': 'Baseball Cap', 'description': 'Casual baseball cap', 'price': 1200, 'stock': 55, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400'},
                {'name': 'Leather Handbag', 'description': 'Elegant leather handbag', 'price': 6500, 'stock': 18, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400'},
                {'name': 'Silk Tie', 'description': 'Premium silk necktie', 'price': 1600, 'stock': 30, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1589756823695-278bc8356c60?w=400'},
                {'name': 'Beanie Hat', 'description': 'Warm knit beanie', 'price': 900, 'stock': 60, 'category_id': accessories_cat.id, 'image_url': 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=400'}
            ]
            
            for prod_data in products_data:
                if not Product.query.filter_by(name=prod_data['name']).first():
                    product = Product(**prod_data)
                    db.session.add(product)
            
            db.session.commit()
            
            return {
                "success": True,
                "message": "Database seeded successfully",
                "data": {
                    "categories": Category.query.count(),
                    "products": Product.query.count(),
                    "admin": "email=admin@shop.com, password=admin123"
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}, 500
    
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from flask import jsonify
    
    @app.route('/api/test-auth')
    @jwt_required()
    def test_auth():
        """Test JWT authentication"""
        try:
            identity = get_jwt_identity()
            return jsonify({
                "message": "JWT is working",
                "identity": identity,
                "identity_type": str(type(identity))
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "https://fashion-clothes-shop-brown.vercel.app",
            "http://localhost:5173",
            "http://localhost:3000"
        ]}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers="*"
    )

    swagger_config = {
        "headers": [], 
        "specs": [{"endpoint": "apispec", "route": "/swagger.json",
                   "rule_filter": lambda rule: True, "model_filter": lambda tag: True}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Fashion Clothes Store",
            "description": "API documentation for the Fashion Clothes Store backend",
            "version": "1.0.0",
            "termsOfService": "http://fashionstore.com/terms",
            "contact": {"name": "Banai Marysah", "url": "https://github.com/Marysah2", "email": "rowwasonga@gmail.com"},
            "license": {"name": "BSD License", "url": "https://opensource.org/licenses/BSD-3-Clause"}
        },
        "basePath": "/api",
        "schemes": ["http", "https"],
        "operationId": "getmyData"
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Register seed command
    from seed import init_app as init_seed
    init_seed(app)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        import sys
        print(f"JWT Error: Token expired. Header: {jwt_header}, Payload: {jwt_payload}", flush=True)
        sys.stdout.flush()
        return {"message": "Token has expired", "error": "token_expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        import sys
        print(f"JWT Error: Invalid token. Error: {str(error)}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        return {"message": "Invalid token", "error": "invalid_token", "details": str(error)}, 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        import sys
        print(f"JWT Error: Missing authorization header. Error: {str(error)}", flush=True)
        sys.stdout.flush()
        return {"message": "Authorization header missing", "error": "authorization_required", "details": str(error)}, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "Token has been revoked", "error": "token_revoked"}, 401

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
