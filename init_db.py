#!/usr/bin/env python3
"""
Database Setup Script
Creates all tables based on your models
"""

from app import create_app
from models import db
from models.user import User
from models.product import Product, Category

def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        print(" Creating database tables...")
        db.create_all()
        print(" Database tables created successfully!")
        
        # Create admin user
        print("\n Creating admin user...")
        admin_email = 'admin@fashion.com'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(f"   Admin user created: {admin_email} / admin123")
        else:
            print(f"   Admin user already exists: {admin_email}")
        
        print("\n Database initialization complete!")
        print("\n Database Summary:")
        print(f"  • Users: {User.query.count()}")
        print(f"  • Categories: {Category.query.count()}")
        print(f"  • Products: {Product.query.count()}")

if __name__ == '__main__':
    init_database()
