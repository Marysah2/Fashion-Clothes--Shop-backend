#!/usr/bin/env python3
"""
Database Setup Script
Creates all tables based on your models
"""

from _init_ import create_app
from extensions import db
from models.user import User, Role
from models.product import Product, Category

def init_database():
    """Initialize database with tables"""
    app = create_app('development')
    
    with app.app_context():
        print("🔄 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create default roles
        print("\n🔄 Creating default roles...")
        roles_data = [
            {'name': 'admin', 'description': 'Administrator with full access'},
            {'name': 'customer', 'description': 'Regular customer'},
            {'name': 'user', 'description': 'Registered user'}
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)
                print(f"  ✓ Created role: {role_data['name']}")
        
        db.session.commit()
        print("✅ Default roles created!")
        
        # Create admin user
        print("\n🔄 Creating admin user...")
        admin_email = 'admin@fashion.com'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            print(f"  ✓ Admin user created: {admin_email} / admin123")
        else:
            print(f"  ℹ Admin user already exists: {admin_email}")
        
        print("\n✅ Database initialization complete!")
        print("\n📊 Database Summary:")
        print(f"  • Users: {User.query.count()}")
        print(f"  • Roles: {Role.query.count()}")
        print(f"  • Categories: {Category.query.count()}")
        print(f"  • Products: {Product.query.count()}")

if __name__ == '__main__':
    init_database()
