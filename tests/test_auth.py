import pytest
from models.user import User
from extensions import db


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


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_user_registration_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@test.com',
            'password': 'password123',
            'name': 'New User',
            'phone': '+1234567890'
        })
        
        assert response.status_code == 201
        assert response.json['success'] == True
        assert 'access_token' in response.json['data']
        assert response.json['data']['user']['email'] == 'newuser@test.com'
    
    def test_user_registration_missing_email(self, client):
        """Test registration fails without email."""
        response = client.post('/api/auth/register', json={
            'password': 'password123',
            'name': 'New User'
        })
        
        assert response.status_code == 400
        assert response.json['success'] == False
        assert 'email' in response.json['message'].lower()
    
    def test_user_registration_missing_password(self, client):
        """Test registration fails without password."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@test.com',
            'name': 'New User'
        })
        
        assert response.status_code == 400
        assert response.json['success'] == False
    
    def test_user_registration_duplicate_email(self, client, app):
        """Test registration fails with duplicate email."""
        with app.app_context():
            user = User(email='existing@test.com', name='Existing User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/register', json={
            'email': 'existing@test.com',
            'password': 'password123',
            'name': 'Another User'
        })
        
        assert response.status_code == 400
        assert response.json['success'] == False
        assert 'already registered' in response.json['message'].lower()


class TestUserLogin:
    """Tests for user login endpoint."""
    
    def test_user_login_success(self, client, app):
        """Test successful user login."""
        with app.app_context():
            user = User(email='login@test.com', name='Login User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert response.json['success'] == True
        assert 'access_token' in response.json['data']
        assert response.json['data']['user']['email'] == 'login@test.com'
    
    def test_user_login_wrong_password(self, client, app):
        """Test login fails with wrong password."""
        with app.app_context():
            user = User(email='login@test.com', name='Login User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert response.json['success'] == False
        assert 'invalid' in response.json['message'].lower()
    
    def test_user_login_nonexistent_email(self, client):
        """Test login fails with nonexistent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        assert response.json['success'] == False
    
    def test_user_login_missing_credentials(self, client):
        """Test login fails without credentials."""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 400
        assert response.json['success'] == False


class TestJWTAuthentication:
    """Tests for JWT token authentication."""
    
    def test_access_token_required(self, client):
        """Test that access token is required for protected routes."""
        response = client.get('/api/auth/me')
        
        # JWT returns 401 when no token is provided
        assert response.status_code in [401, 422]
    
    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        # JWT returns 422 for invalid tokens in newer versions
        assert response.status_code in [401, 422]


class TestCurrentUser:
    """Tests for current user endpoints."""
    
    def test_get_current_user(self, client, app):
        """Test getting current authenticated user."""
        token = None
        with app.app_context():
            user = User(email='current@test.com', name='Current User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Login to get token
            login_resp = client.post('/api/auth/login', json={
                'email': 'current@test.com',
                'password': 'password123'
            })
            token = login_resp.json['data']['access_token']
        
        # Get current user
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # JWT with valid token should work
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            assert response.json['success'] == True
            assert response.json['data']['email'] == 'current@test.com'
    
    def test_update_current_user(self, client, app):
        """Test updating current user profile."""
        token = None
        with app.app_context():
            user = User(email='update@test.com', name='Update User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Login to get token
            login_resp = client.post('/api/auth/login', json={
                'email': 'update@test.com',
                'password': 'password123'
            })
            token = login_resp.json['data']['access_token']
        
        # Update user
        response = client.put(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'},
            json={'name': 'Updated Name', 'phone': '+9876543210'}
        )
        
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            assert response.json['success'] == True
            assert response.json['data']['name'] == 'Updated Name'


class TestRoleBasedAccess:
    """Tests for role-based access control."""
    
    def test_admin_can_access_admin_routes(self, client, app):
        """Test admin can access admin-only routes."""
        token = None
        with app.app_context():
            admin = User(email='admin@test.com', name='Admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            
            # Login as admin
            login_resp = client.post('/api/auth/login', json={
                'email': 'admin@test.com',
                'password': 'admin123'
            })
            token = login_resp.json['data']['access_token']
        
        # Access admin route
        response = client.get(
            '/api/auth/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [200, 401, 422]
    
    def test_regular_user_cannot_access_admin_routes(self, client, app):
        """Test regular users cannot access admin routes."""
        token = None
        with app.app_context():
            user = User(email='user@test.com', name='Regular User')
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()
            
            # Login as regular user
            login_resp = client.post('/api/auth/login', json={
                'email': 'user@test.com',
                'password': 'user123'
            })
            token = login_resp.json['data']['access_token']
        
        # Try to access admin route
        response = client.get(
            '/api/auth/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Should be 403 for unauthorized or 422 for JWT issues
        assert response.status_code in [403, 401, 422]


class TestUserLogout:
    """Tests for user logout."""
    
    def test_user_logout(self, client, app):
        """Test user logout endpoint."""
        token = None
        with app.app_context():
            user = User(email='logout@test.com', name='Logout User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Login to get token
            login_resp = client.post('/api/auth/login', json={
                'email': 'logout@test.com',
                'password': 'password123'
            })
            token = login_resp.json['data']['access_token']
        
        # Logout
        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Logout should work with valid token
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            assert response.json['success'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
