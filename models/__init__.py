from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""
Models package
"""

from models.user import User
from models.product import Product, Category
from models.cart import Cart, CartItem, Invoice
from models.order import Order, OrderItem

__all__ = ['User', 'Product', 'Category', 'Cart', 'CartItem', 'Invoice', 'Order', 'OrderItem']