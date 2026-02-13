"""
Analytics routes
Provides admin analytics dashboard
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from services.analytics_service import get_admin_analytics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/orders/admin')


@analytics_bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics():
    """
    Admin: Get comprehensive analytics dashboard
    ---
    tags:
      - Analytics
    summary: Get admin analytics dashboard
    description: Returns comprehensive analytics data including revenue trends, orders trends, and category statistics.
    responses:
      200:
        description: Analytics data retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    ordersTrend:
                      type: array
                      items:
                        type: object
                        properties:
                          date:
                            type: string
                            example: "2026-02-12"
                          totalOrders:
                            type: integer
                            example: 5
                    revenueTrend:
                      type: array
                      items:
                        type: object
                        properties:
                          date:
                            type: string
                            example: "2026-02-12"
                          revenue:
                            type: number
                            format: float
                            example: 1500.5
                    categoryStatistics:
                      type: array
                      items:
                        type: object
                        properties:
                          category:
                            type: string
                            example: Electronics
                          totalOrders:
                            type: integer
                            example: 10
                          revenue:
                            type: number
                            format: float
                            example: 2500.0
      500:
        description: Analytics generation failed
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: Analytics generation failed
                error:
                  type: string
                  example: "Database connection error"
    """
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