from flask import Flask
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

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "Token has expired", "error": "token_expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "Invalid token", "error": "invalid_token", "details": str(error)}, 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
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
    app.run(debug=True)
