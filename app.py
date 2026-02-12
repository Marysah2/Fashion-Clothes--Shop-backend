from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from models import db
from models.tokenblacklist import TokenBlacklist

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # CORS setup
    CORS(
        app,
        origins=[
            "https://fashion-clothes-shop-brown.vercel.app",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        supports_credentials=True,
        allow_headers="*",
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Register blueprints
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

    # Swagger config
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

    # JWT token check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None

    return app