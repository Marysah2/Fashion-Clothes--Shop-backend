# Analytics tests
# Tests for analytics endpoints

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _init_ import create_app
from extensions import db
from models.user import User, Role
from models.order import Order, OrderItem


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


class TestAnalyticsAuthentication:
    """Tests for analytics authentication."""
    
    def test_analytics_requires_authentication(self, client):
        """Test unauthenticated users cannot access analytics."""
        response = client.get('/api/orders/admin/analytics')
        # Should be 401 or 422 without token
        assert response.status_code in [401, 422]


class TestAnalyticsEndpoints:
    """Tests for analytics endpoint structure."""
    
    def test_analytics_endpoint_exists(self, client):
        """Test analytics endpoint exists (will return auth error)."""
        response = client.get('/api/orders/admin/analytics')
        # Just verify endpoint exists
        assert response.status_code in [401, 422, 200]
    
    def test_total_orders_analytics_endpoint_exists(self, client):
        """Test total orders endpoint exists."""
        response = client.get('/api/orders/analytics/total')
        assert response.status_code in [401, 422, 200]
    
    def test_revenue_analytics_endpoint_exists(self, client):
        """Test revenue analytics endpoint exists."""
        response = client.get('/api/orders/analytics/revenue')
        assert response.status_code in [401, 422, 200]
    
    def test_category_analytics_endpoint_exists(self, client):
        """Test category analytics endpoint exists."""
        response = client.get('/api/orders/analytics/categories')
        assert response.status_code in [401, 422, 200]


class TestOrderRetrieval:
    """Tests for order retrieval endpoints."""
    
    def test_get_user_orders_requires_auth(self, client):
        """Test getting user orders requires authentication."""
        response = client.get('/api/orders/my-orders')
        assert response.status_code in [401, 422]
    
    def test_get_all_orders_admin_requires_auth(self, client):
        """Test getting all orders requires admin authentication."""
        response = client.get('/api/orders/admin/all')
        assert response.status_code in [401, 422]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
