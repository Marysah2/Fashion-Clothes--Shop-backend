from datetime import datetime, timedelta
from sqlalchemy import func, cast, Numeric, extract, text
from sqlalchemy.dialects.postgresql import JSONB
from extensions import db
from models.order import Order

def get_admin_analytics():
    """Generate comprehensive analytics using PostgreSQL aggregations"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # ===== 1. SUMMARY STATISTICS =====
    summary = db.session.query(
        func.count(Order.id).label('total_orders'),
        func.coalesce(func.sum(Order.total_amount), 0).label('total_revenue'),
        func.coalesce(func.avg(Order.total_amount), 0).label('avg_order_value'),
        func.sum(func.cast(Order.status == 'pending', db.Integer)).label('pending_orders')
    ).filter(Order.created_at >= thirty_days_ago).first()
    
    # ===== 2. ORDERS TREND (Last 30 days) =====
    orders_trend = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count')
    ).filter(
        Order.created_at >= thirty_days_ago
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # ===== 3. REVENUE TREND (Last 30 days) =====
    revenue_trend = db.session.query(
        func.date(Order.created_at).label('date'),
        func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
    ).filter(
        Order.created_at >= thirty_days_ago
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # ===== 4. STATUS DISTRIBUTION =====
    status_dist = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).filter(
        Order.created_at >= thirty_days_ago
    ).group_by(Order.status).all()
    
    # ===== 5. CATEGORY-LEVEL STATISTICS (Using JSONB aggregation) =====
    # CRITICAL: Requires items JSONB to contain 'category_name' field
    category_stats = db.session.execute(
        text("""
        SELECT 
            elem->>'category_name' AS category,
            COUNT(*) AS order_count,
            SUM((elem->>'price')::numeric * (elem->>'quantity')::numeric) AS total_revenue
        FROM orders o
        CROSS JOIN LATERAL jsonb_array_elements(o.items) AS elem
        WHERE o.created_at >= :thirty_days_ago
        GROUP BY elem->>'category_name'
        ORDER BY total_revenue DESC
        """),
        {'thirty_days_ago': thirty_days_ago}
    ).fetchall()
    
    # Format results for frontend
    return {
        'summary': {
            'totalOrders': int(summary.total_orders),
            'totalRevenue': float(summary.total_revenue),
            'avgOrderValue': float(round(summary.avg_order_value, 2)),
            'pendingOrders': int(summary.pending_orders or 0)
        },
        'ordersTrend': [
            {'date': str(r.date), 'count': r.count} 
            for r in orders_trend
        ],
        'revenueTrend': [
            {'date': str(r.date), 'revenue': float(r.revenue)} 
            for r in revenue_trend
        ],
        'statusDistribution': [
            {'status': r.status, 'count': r.count} 
            for r in status_dist
        ],
        'categoryStatistics': [
            {
                'category': r.category, 
                'count': int(r.order_count),
                'revenue': float(r.total_revenue)
            } 
            for r in category_stats if r.category
        ]
    }

def get_user_orders(user_id):
    """Get orders for specific user (customer view)"""
    return Order.query.filter_by(user_id=user_id)\
        .order_by(Order.created_at.desc())\
        .all()

def get_all_orders_admin(status=None, start_date=None, end_date=None):
    """Get all orders with optional filters (admin view)"""
    query = Order.query
    
    if status:
        query = query.filter(Order.status == status)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    return query.order_by(Order.created_at.desc()).all()