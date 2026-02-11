import pytest
from app import create_app, db
from app.models.order import Order, OrderItem

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

def test_create_order(client):
    response = client.post('/api/orders/', json={
        'cart_items': [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ],
        'shipping_address': {
            'street': '123 Main St',
            'city': 'New York',
            'zip': '10001'
        },
        'billing_info': {
            'card_number': '****1234',
            'name': 'John Doe'
        }
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Order placed successfully'
    assert 'order_id' in data
    assert 'invoice_number' in data
    assert data['status'] == 'completed'
    assert 'invoice' in data

def test_create_order_missing_cart_items(client):
    response = client.post('/api/orders/', json={
        'shipping_address': {'street': '123 Main St'}
    })
    assert response.status_code == 400

def test_create_order_empty_cart(client):
    response = client.post('/api/orders/', json={
        'cart_items': [],
        'shipping_address': {'street': '123 Main St'}
    })
    assert response.status_code == 400

def test_get_order(client):
    create_response = client.post('/api/orders/', json={
        'cart_items': [{'product_id': 1, 'quantity': 2}],
        'shipping_address': {'street': '123 Main St'}
    })
    order_id = create_response.get_json()['order_id']
    
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['order_id'] == order_id

def test_get_nonexistent_order(client):
    response = client.get('/api/orders/999')
    assert response.status_code == 404

def test_invoice_generation(client):
    response = client.post('/api/orders/', json={
        'cart_items': [{'product_id': 1, 'quantity': 2}],
        'shipping_address': {'street': '123 Main St'}
    })
    
    data = response.get_json()
    assert data['invoice_number'].startswith('INV-')
    assert len(data['invoice_number']) == 16
