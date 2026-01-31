
# Fashion Clothes Shop - Backend

## Project Structure

```
Fashion-Clothes--Shop---backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── models/              # Database models
│   ├── user.py         # User & Role models (Banai)
│   ├── product.py      # Product & Category models (Kabathi)
│   ├── cart.py         # Cart & Invoice models (Sharon)
│   └── order.py        # Order models (Amos)
├── routes/              # API endpoints
│   ├── auth.py         # Authentication routes (Banai)
│   ├── products.py     # Product catalog routes (Kabathi)
│   ├── cart.py         # Cart & checkout routes (Sharon)
│   ├── orders.py       # Orders & analytics routes (Amos)
│   └── admin.py        # Admin management routes
├── utils/               # Utility functions
│   ├── decorators.py   # Auth decorators
│   └── error_handlers.py # Global error handling (Edward)
└── tests/               # Test files
    ├── test_auth.py    # Authentication tests (Banai)
    ├── test_products.py # Product tests (Kabathi)
    ├── test_cart.py    # Cart tests (Sharon)
    └── test_analytics.py # Analytics tests (Amos)
```

## Team Assignments

### Banai - Authentication & User Management
- Files: `models/user.py`, `routes/auth.py`, `tests/test_auth.py`
- Tasks: User registration, login, JWT auth, role-based access control

### Kabathi - Product Catalog & Categories  
- Files: `models/product.py`, `routes/products.py`, `tests/test_products.py`
- Tasks: Product/category models, CRUD endpoints, image serving, filtering

### Sharon - Cart & Checkout Flow
- Files: `models/cart.py`, `routes/cart.py`, `tests/test_cart.py`  
- Tasks: Cart operations, checkout flow, payment simulation

### Amos - Orders & Customer Analytics
- Files: `models/order.py`, `routes/orders.py`, `tests/test_analytics.py`
- Tasks: Order retrieval, analytics endpoints, data aggregation

### Edward - Infrastructure & Testing
- Files: `utils/error_handlers.py`, API documentation, CI/CD setup
- Tasks: Global error handling, logging, test coverage, documentation

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure database settings
3. Run the application: `python app.py`
4. Database tables will be created automatically on first run

## Database Setup

Configure PostgreSQL connection in `.env`:
```
DATABASE_URL=postgresql://username:password@localhost/fashion_shop
```