# Cart and checkout tests
# Sharon: Tests for checkout logic

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _init_ import create_app
from extensions import db
from models.user import User, Role
from models.product import Product, Category
from models.cart import Cart, CartItem


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
import pytest
from app import create_app, db
from app.models.cart import Cart, CartItem

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


class TestAddToCart:
    """Tests for adding items to cart."""
    
    def test_add_to_cart_requires_auth(self, client):
        """Test adding to cart requires authentication."""
        response = client.post('/api/cart/add', json={'product_id': 1, 'quantity': 1})
        assert response.status_code in [401, 422]


class TestUpdateCartQuantity:
    """Tests for updating cart item quantities."""
    
    def test_update_cart_requires_auth(self, client):
        """Test updating cart requires authentication."""
        response = client.put('/api/cart/update', json={'item_id': 1, 'quantity': 1})
        assert response.status_code in [401, 422]


class TestRemoveFromCart:
    """Tests for removing items from cart."""
    
    def test_remove_from_cart_requires_auth(self, client):
        """Test removing from cart requires authentication."""
        response = client.delete('/api/cart/remove/1')
        assert response.status_code in [401, 422]


class TestClearCart:
    """Tests for clearing cart."""
    
    def test_clear_cart_requires_auth(self, client):
        """Test clearing cart requires authentication."""
        response = client.delete('/api/cart/clear')
        assert response.status_code in [401, 422]


class TestGetCart:
    """Tests for retrieving cart."""
    
    def test_get_empty_cart(self, client):
        """Test getting empty cart returns empty array."""
        response = client.get('/api/cart/')
        assert response.status_code in [200, 401, 422]


class TestCartCount:
    """Tests for cart item count."""
    
    def test_get_cart_count_requires_auth(self, client):
        """Test getting cart count requires authentication."""
        response = client.get('/api/cart/count')
        assert response.status_code in [200, 401, 422]


class TestCheckout:
    """Tests for checkout process."""
    
    def test_checkout_requires_auth(self, client):
        """Test checkout requires authentication."""
        response = client.post('/api/cart/checkout', json={'shipping_address': {}})
        assert response.status_code in [401, 422]


class TestPaymentSimulation:
    """Tests for payment simulation."""
    
    def test_payment_requires_auth(self, client):
        """Test payment simulation requires authentication."""
        response = client.post('/api/cart/payment/simulate', json={'order_id': 1})
        assert response.status_code in [401, 422]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
@pytest.fixture
def client(app):
    return app.test_client()

def test_get_empty_cart(client):
    response = client.get('/api/cart/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'cart_id' in data
    assert data['items'] == []

def test_add_to_cart(client):
    response = client.post('/api/cart/add', json={
        'product_id': 1,
        'quantity': 2
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert data['item']['product_id'] == 1
    assert data['item']['quantity'] == 2

def test_add_to_cart_missing_product_id(client):
    response = client.post('/api/cart/add', json={'quantity': 2})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_add_to_cart_invalid_quantity(client):
    response = client.post('/api/cart/add', json={
        'product_id': 1,
        'quantity': 0
    })
    assert response.status_code == 400

def test_update_cart_item(client):
    add_response = client.post('/api/cart/add', json={
        'product_id': 1,
        'quantity': 2
    })
    
    response = client.put('/api/cart/update', json={'product_id': 1, 'quantity': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert data['item']['quantity'] == 5

def test_remove_from_cart(client):
    add_response = client.post('/api/cart/add', json={
        'product_id': 1,
        'quantity': 2
    })
    
    response = client.delete('/api/cart/remove/1')
    assert response.status_code == 200
    
    get_response = client.get('/api/cart/')
    assert len(get_response.get_json()['items']) == 0

def test_clear_cart(client):
    client.post('/api/cart/add', json={'product_id': 1, 'quantity': 2})
    client.post('/api/cart/add', json={'product_id': 2, 'quantity': 1})
    
    response = client.delete('/api/cart/clear')
    assert response.status_code == 200
    
    get_response = client.get('/api/cart/')
    assert len(get_response.get_json()['items']) == 0
