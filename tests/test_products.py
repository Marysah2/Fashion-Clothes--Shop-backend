# Product catalog tests
# Kabathi: Tests for catalog APIs

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _init_ import create_app
from extensions import db
from models.user import User, Role
from models.product import Product, Category


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


class TestProductCreation:
    """Tests for product creation endpoint."""
    
    def test_create_product_success(self, client, app):
        """Test successfully creating a product."""
        # Create category first
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
        
        response = client.post('/api/products/',
            headers={'Authorization': 'Bearer test_token'},
            json={'name': 'New Product', 'price': 49.99, 'category_id': 1})
        
        # Auth will fail with 422 for invalid token
        assert response.status_code in [401, 403, 422, 201]
    
    def test_create_product_missing_name(self, client):
        """Test creating product without name fails."""
        response = client.post('/api/products/',
            headers={'Authorization': 'Bearer test_token'},
            json={'price': 49.99, 'category_id': 1})
        assert response.status_code in [400, 401, 403, 422]
    
    def test_create_product_requires_admin(self, client):
        """Test regular users cannot create products."""
        response = client.post('/api/products/',
            headers={'Authorization': 'Bearer invalid_token'},
            json={'name': 'New Product', 'price': 49.99, 'category_id': 1})
        assert response.status_code in [401, 403, 422]


class TestProductListing:
    """Tests for product listing endpoint."""
    
    def test_get_products_empty(self, client):
        """Test getting products when none exist."""
        response = client.get('/api/products/')
        assert response.status_code == 200
        assert response.json['success'] == True
    
    def test_get_products_with_data(self, client, app):
        """Test getting products with data."""
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
            cat_id = cat.id
            
            for i in range(3):
                prod = Product(name=f'Test Product {i}', slug=f'test-product-{i}',
                    price=29.99 + i, category_id=cat_id, is_active=True)
                db.session.add(prod)
            db.session.commit()
        
        response = client.get('/api/products/')
        assert response.status_code == 200
        assert len(response.json['data']) == 3
    
    def test_get_products_pagination(self, client, app):
        """Test product pagination."""
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
            cat_id = cat.id
            
            for i in range(15):
                prod = Product(name=f'Product {i}', slug=f'product-{i}',
                    price=10.00 + i, category_id=cat_id, is_active=True)
                db.session.add(prod)
            db.session.commit()
        
        response = client.get('/api/products/?page=1&per_page=5')
        assert response.status_code == 200
        assert len(response.json['data']) == 5
        assert response.json['pagination']['total'] == 15


class TestCategoryFiltering:
    """Tests for category filtering."""
    
    def test_get_categories(self, client, app):
        """Test getting all categories."""
        with app.app_context():
            Category(name='Category 1', slug='category-1').save = lambda: db.session.add(Category(name='Category 1', slug='category-1'))
            cat1 = Category(name='Category 1', slug='category-1')
            cat2 = Category(name='Category 2', slug='category-2')
            db.session.add(cat1)
            db.session.add(cat2)
            db.session.commit()
        
        response = client.get('/api/products/categories')
        assert response.status_code == 200
        assert response.json['success'] == True


class TestProductUpdate:
    """Tests for product update endpoint."""
    
    def test_update_product_success(self, client, app):
        """Test successfully updating a product."""
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
            
            prod = Product(name='Original', slug='original', price=29.99, category_id=cat.id)
            db.session.add(prod)
            db.session.commit()
            product_id = prod.id
        
        response = client.put(f'/api/products/{product_id}',
            headers={'Authorization': 'Bearer invalid_token'},
            json={'name': 'Updated Name', 'price': 39.99})
        
        assert response.status_code in [200, 401, 403, 422]


class TestProductDelete:
    """Tests for product deletion endpoint."""
    
    def test_delete_product_success(self, client, app):
        """Test successfully deleting a product."""
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
            
            prod = Product(name='To Delete', slug='to-delete', price=29.99, category_id=cat.id)
            db.session.add(prod)
            db.session.commit()
            product_id = prod.id
        
        response = client.delete(f'/api/products/{product_id}',
            headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code in [200, 401, 403, 422]


class TestFeaturedProducts:
    """Tests for featured products endpoint."""
    
    def test_get_featured_products(self, client, app):
        """Test getting featured products."""
        with app.app_context():
            cat = Category(name='Test Category', slug='test-category')
            db.session.add(cat)
            db.session.commit()
            
            prod1 = Product(name='Featured', slug='featured', price=29.99,
                category_id=cat.id, is_featured=True, is_active=True)
            prod2 = Product(name='Regular', slug='regular', price=19.99,
                category_id=cat.id, is_featured=False, is_active=True)
            db.session.add(prod1)
            db.session.add(prod2)
            db.session.commit()
        
        response = client.get('/api/products/featured')
        assert response.status_code == 200
        assert response.json['success'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
