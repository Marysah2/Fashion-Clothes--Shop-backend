from flask_migrate import Migrate
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db
from models.tokenblacklist import TokenBlacklist
from flasgger import Swagger


jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
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



    
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/swagger.json',   
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True
            }
        ],
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
            "contact": {
                "name": "Banai Marysah",
                "url": "https://github.com/Marysah2",
                "email": "banaimarysah@gmail.com"
            },
            "license": {
                "name": "BSD License",
                "url": "https://opensource.org/licenses/BSD-3-Clause"
            }
        },
        "host": "127.0.0.1:5000",  
        "basePath": "/api",
        "schemes": ["http", "https"],
        "operationId": "getmyData"
    }

    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None
    
    return app
app = create_app()

if __name__ == '__main__':
    
    app.run(debug=True)