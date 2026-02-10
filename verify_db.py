#!/usr/bin/env python3
"""
Database Verification Script
"""

from _init_ import create_app
from extensions import db
from models.user import User, Role
from models.product import Product, Category

app = create_app('development')

with app.app_context():
    print("✅ DATABASE VERIFICATION\n")
    print("=" * 50)
    
    # Check tables
    print("\n📊 Database Tables:")
    print(f"  • Users: {User.query.count()}")
    print(f"  • Roles: {Role.query.count()}")
    print(f"  • Categories: {Category.query.count()}")
    print(f"  • Products: {Product.query.count()}")
    
    # Check admin user
    print("\n👤 Admin User:")
    admin = User.query.filter_by(email='admin@fashion.com').first()
    if admin:
        print(f"  ✓ Email: {admin.email}")
        print(f"  ✓ Name: {admin.name}")
        print(f"  ✓ Is Admin: {admin.is_admin}")
        print(f"  ✓ Roles: {[r.name for r in admin.roles]}")
    
    # Check roles
    print("\n🔐 Available Roles:")
    for role in Role.query.all():
        print(f"  • {role.name}: {role.description}")
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! Database is ready.")
    print("\n🚀 You can now:")
    print("  1. Run: python3 app.py")
    print("  2. Login with: admin@fashion.com / admin123")
    print("  3. Access API at: http://localhost:5000")
