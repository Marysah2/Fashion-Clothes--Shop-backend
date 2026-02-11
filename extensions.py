"""
Flask Extensions Module
Initializes database, JWT, CORS, and migrations
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

# Configure JWT
jwt_config = {
    'JWT_TOKEN_LOCATION': ['headers'],
    'JWT_HEADER_NAME': 'Authorization',
    'JWT_HEADER_TYPE': 'Bearer',
    'JWT_ERROR_MESSAGE_KEY': 'message',
}
