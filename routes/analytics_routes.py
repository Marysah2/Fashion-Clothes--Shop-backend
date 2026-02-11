from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from services.analytics_service import get_admin_analytics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/orders/admin')

@analytics_bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics():
    """Admin analytics dashboard endpoint"""
    try:
        analytics_data = get_admin_analytics()
        return jsonify({
            'success': True,
            'data': analytics_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Analytics generation failed',
            'error': str(e)
        }), 500