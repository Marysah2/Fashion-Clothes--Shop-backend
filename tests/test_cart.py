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
