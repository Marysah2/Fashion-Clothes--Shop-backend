"""
Fashion Clothes Shop Backend Application
Flask REST API with PostgreSQL, JWT Authentication
"""

import os
from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, migrate, jwt_config

def create_app(config_name='development'):
    """Application factory pattern for Flask app"""
    from config import config
    
    app = Flask(__name__)
    
    # Load configuration
    if isinstance(config_name, str) and config_name in config:
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config.get('default', config['development']))
    
    # Apply JWT config
    app.config.update(jwt_config)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp
    from routes.analytics_routes import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(analytics_bp)
    
    # Register error handlers
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Fashion Clothes Shop API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
