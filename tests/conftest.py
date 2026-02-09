"""
Pytest configuration and fixtures for testing
"""

import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _init_ import create_app
from extensions import db
from models.user import User, Role


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    application = create_app('testing')
    application.config['TESTING'] = True
    
    with application.app_context():
        db.create_all()
        # Create default roles
        customer_role = Role(name='customer', description='Regular customer')
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(customer_role)
        db.session.add(admin_role)
        db.session.commit()
        
        yield application
        
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def admin_token(client, app):
    """Create admin user and return JWT token."""
    with app.app_context():
        admin = User(email='admin@test.com', name='Admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        resp = client.post('/api/auth/login',
                          json={'email': 'admin@test.com', 'password': 'admin123'})
        return resp.json['data']['access_token']


@pytest.fixture(scope='session')
def user_token(client, app):
    """Create regular user and return JWT token."""
    with app.app_context():
        user = User(email='user@test.com', name='Regular User', is_admin=False)
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()
        
        resp = client.post('/api/auth/login',
                          json={'email': 'user@test.com', 'password': 'user123'})
        return resp.json['data']['access_token']
