"""
Global error handling and logging utilities
Implements global error handlers and logging configuration
"""

from flask import jsonify
import logging

def register_error_handlers(app):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Unauthorized',
            'error': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Forbidden',
            'error': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Not found',
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed',
            'error': 'This method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred'
        }), 500

def setup_logging(app):
    """Configure logging for the Flask application"""
    
    # Create logs directory if it doesn't exist
    import os
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    return app
