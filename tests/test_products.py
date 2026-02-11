# Product catalog tests
# Kabathi: Tests for catalog APIsa

import unittest
from app import create_app, db
from models.product import Product, Category
from models.user import User

class TestProducts(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            admin_user = User(email='admin@test.com', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            category = Category(name='T-Shirts', description='Casual t-shirts')
            db.session.add(category)
            db.session.commit()
            
            self.category_id = category.id
            
            response = self.client.post('/api/auth/login', json={
                'email': 'admin@test.com',
                'password': 'admin123'
            })
            self.admin_token = response.get_json()['access_token']
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_product_creation(self):
        response = self.client.post('/api/products/', 
            json={'name': 'Blue T-Shirt', 'price': 29.99, 'stock': 50, 'category_id': self.category_id},
            headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['name'], 'Blue T-Shirt')
    
    def test_product_listing(self):
        with self.app.app_context():
            product = Product(name='Red Shirt', price=25.00, stock=10, category_id=self.category_id)
            db.session.add(product)
            db.session.commit()
        
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)
    
    def test_category_filtering(self):
        with self.app.app_context():
            product = Product(name='Green Shirt', price=30.00, stock=15, category_id=self.category_id)
            db.session.add(product)
            db.session.commit()
        
        response = self.client.get(f'/api/products/?category_id={self.category_id}')
        self.assertEqual(response.status_code, 200)
        products = response.get_json()
        self.assertTrue(all(p['category_id'] == self.category_id for p in products))
    
    def test_image_serving(self):
        response = self.client.get('/api/products/images/test.jpg')
        self.assertIn(response.status_code, [200, 404])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
