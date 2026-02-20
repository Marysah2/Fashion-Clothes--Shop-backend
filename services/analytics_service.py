from datetime import datetime, timedelta
from sqlalchemy import func, cast, Numeric, extract, text
from extensions import db
from models.order import Order
import json

def get_admin_analytics():
    """Generate comprehensive analytics compatible with SQLite and PostgreSQL"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # ===== 1. SUMMARY STATISTICS =====
    summary = db.session.query(
        func.count(Order.id).label('total_orders'),
        func.coalesce(func.sum(Order.total_amount), 0).label('total_revenue'),
        func.coalesce(func.avg(Order.total_amount), 0).label('avg_order_value')
    ).filter(Order.created_at >= thirty_days_ago).first()
    
    pending_count = Order.query.filter(
        Order.created_at >= thirty_days_ago,
        Order.status == 'pending'
    ).count()
    
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
    
    # ===== 5. CATEGORY-LEVEL STATISTICS (Python-based for SQLite compatibility) =====
    orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()
    category_stats = {}
    
    for order in orders:
        items = json.loads(order.items) if isinstance(order.items, str) else order.items
        for item in items:
            category = item.get('category_name', 'Uncategorized')
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'revenue': 0}
            category_stats[category]['count'] += 1
            category_stats[category]['revenue'] += float(item.get('price', 0)) * int(item.get('quantity', 0))
    
    # Format results for frontend
    return {
        'summary': {
            'totalOrders': int(summary.total_orders),
            'totalRevenue': float(summary.total_revenue),
            'avgOrderValue': float(round(summary.avg_order_value, 2)),
            'pendingOrders': pending_count
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
            {'category': cat, 'count': stats['count'], 'revenue': stats['revenue']}
            for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)
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