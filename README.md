
# Fashion & Clothes Shop - E-Commerce Platform

## 📋 Project Overview

A modern, fashionable clothing e-commerce platform designed to provide a unique and compelling online shopping experience for fashion-conscious customers. This full-stack application combines a React frontend with a Flask backend, offering seamless product browsing, cart management, secure checkout, and comprehensive admin analytics.

## 🎯 Problem Statement

The online fashion retail market is highly competitive with numerous established players. This platform addresses key challenges:

- **Market Differentiation**: Standing out in a crowded marketplace by offering a curated, trendy clothing collection
- **Visual Engagement**: Showcasing products in an appealing, visually engaging manner
- **Product Information**: Providing accurate sizing, fit, and fabric details for customer satisfaction
- **User Experience**: Optimizing across all devices with mobile-first design
- **Trust & Security**: Implementing secure payments, reliable shipping, and robust customer support
- **Sales Generation**: Converting visitors into customers through intuitive shopping flows

## ✨ MVP Features

### Customer Features
- **Authentication**: User registration and login with JWT-based security
- **Product Catalog**: Browse fashion items organized by categories
- **Product Details**: View comprehensive product information (images, descriptions, sizing, materials)
- **Shopping Cart**: Add, update, and remove items with real-time cart management
- **Checkout Process**: Complete orders with simulated payment processing
- **Order History**: Track past purchases and order status
- **Filtering & Sorting**: Find products by category, price, and other attributes

### Admin Features
- **Product Management**: Full CRUD operations for fashion products and categories
- **User Management**: Role-based access control and user administration
- **Product Analytics**: View metrics on product performance (views, cart additions, sales)
- **Order Analytics**: Monitor orders, revenue trends, and category statistics
- **Dashboard**: Comprehensive analytics with charts and data visualizations

### Payment Simulation
- Internally generates billing addresses, shipping information, and invoices
- Creates order records with complete transaction details
- No external payment gateway integration (MVP scope)

## 🛠️ Technical Stack

### Backend
- **Framework**: Python Flask 2.3.3
- **Database**: PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **ORM**: SQLAlchemy
- **Testing**: Minitest (unittest)
- **API**: RESTful architecture

### Frontend
- **Framework**: React.js
- **State Management**: Redux Toolkit
- **Testing**: Jest
- **Design**: Figma wireframes (mobile-first)
- **Styling**: Responsive, mobile-friendly UI

### Development Tools
- **Version Control**: Git
- **API Documentation**: Swagger/Postman
- **Environment**: Python virtual environment

## 📁 Project Structure

```
Fashion-Clothes--Shop---backend/
├── app.py                 # Main Flask application entry point
├── config.py             # Configuration settings (DB, JWT, etc.)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
│
├── models/              # Database models (SQLAlchemy)
│   ├── __init__.py
│   ├── user.py         # User & Role models (Banai)
│   ├── product.py      # Product & Category models (Kabathi)
│   ├── cart.py         # Cart & Invoice models (Sharon)
│   └── order.py        # Order & OrderItem models (Amos)
│
├── routes/              # API endpoints (Flask Blueprints)
│   ├── __init__.py
│   ├── auth.py         # Authentication routes (Banai)
│   ├── products.py     # Product catalog routes (Kabathi)
│   ├── cart.py         # Cart & checkout routes (Sharon)
│   ├── orders.py       # Orders & analytics routes (Amos)
│   └── admin.py        # Admin management routes
│
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── decorators.py   # Auth decorators (login_required, admin_required)
│   └── error_handlers.py # Global error handling (Edward)
│
└── tests/               # Test suite
    ├── __init__.py
    ├── test_auth.py    # Authentication tests (Banai)
    ├── test_products.py # Product tests (Kabathi)
    ├── test_cart.py    # Cart tests (Sharon)
    └── test_analytics.py # Analytics tests (Amos)
```

## 👥 Team Assignments

### Banai - Authentication & User Management
**Backend Files**: `models/user.py`, `routes/auth.py`, `tests/test_auth.py`
- User registration with validation
- Login with JWT token generation
- Token refresh mechanism
- Role-based access control (Customer, Admin)
- User CRUD operations for admin

**Frontend Tasks**:
- Login and Create Account pages
- Redux slices for authentication state
- Protected routes and session handling
- User-role management UI for admin panel

### Kabathi - Product Catalog & Categories
**Backend Files**: `models/product.py`, `routes/products.py`, `tests/test_products.py`
- Product and Category database models
- CRUD endpoints for products (admin only)
- Product listing with filtering/sorting
- Category management
- Image serving functionality

**Frontend Tasks**:
- Item listing pages (category-based)
- Product detail page (images, description, sizing, material)
- Filtering & sorting UI
- Admin interface for product catalog management

### Sharon - Cart & Checkout Flow
**Backend Files**: `models/cart.py`, `routes/cart.py`, `tests/test_cart.py`
- Cart and CartItem models
- Add/remove/update cart endpoints
- Checkout process implementation
- Payment simulation (generate invoices, billing data)
- Order creation from cart

**Frontend Tasks**:
- Cart page with quantity edits and removal
- Checkout form UI (address, billing simulation, summary)
- Order confirmation page
- Redux slices for cart and checkout flows

### Amos - Orders & Customer Analytics
**Backend Files**: `models/order.py`, `routes/orders.py`, `tests/test_analytics.py`
- Order and OrderItem models
- Order retrieval endpoints (customer & admin)
- Analytics endpoints (total orders, revenue, category stats)
- PostgreSQL data aggregation queries
- Time-series analytics

**Frontend Tasks**:
- Customer order history page
- Admin dashboards for order analytics
- Responsive data visualizations (charts, trends)
- Chart library integration

### Edward - Infrastructure & Testing
**Backend Files**: `utils/error_handlers.py`, API documentation
- Global error handling and logging
- API documentation (Swagger/Postman)
- CI/CD pipeline setup
- Test coverage metrics
- Backend integration assistance

**Frontend Tasks**:
- Figma wireframing (mobile-first)
- Consistent UI components across pages
- Reusable layout components (navbar, footer, theme)
- Responsive design implementation
- Frontend performance optimization
- Jest tests for UI components

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- Virtual environment tool (venv)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Fashion-Clothes--Shop---backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Setup PostgreSQL database**
```bash
# Create database
psql -U postgres
CREATE DATABASE fashion_shop;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE fashion_shop TO myuser;
\q
```

6. **Run the application**
```bash
python app.py
```

The server will start at `http://localhost:5000`

### Database Configuration

Update `.env` file with your PostgreSQL credentials:
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/fashion_shop
FLASK_ENV=development
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_auth

# Run with coverage
pip install coverage
coverage run -m unittest discover tests
coverage report
```

## 📡 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /refresh` - Refresh JWT token
- `POST /logout` - User logout

### Products (`/api/products`)
- `GET /` - List all products (with filtering/sorting)
- `GET /<id>` - Get single product
- `POST /` - Create product (admin)
- `PUT /<id>` - Update product (admin)
- `DELETE /<id>` - Delete product (admin)
- `GET /categories` - List categories
- `GET /images/<filename>` - Serve product images

### Cart (`/api/cart`)
- `GET /` - Get user's cart
- `POST /add` - Add item to cart
- `PUT /update` - Update cart item quantity
- `DELETE /remove/<id>` - Remove item from cart
- `POST /checkout` - Process checkout
- `POST /payment/simulate` - Simulate payment

### Orders (`/api/orders`)
- `GET /` - Get user's order history
- `GET /<id>` - Get single order details
- `GET /analytics/total` - Total orders over time
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/categories` - Category statistics

### Admin (`/api/admin`)
- `GET /users` - List all users
- `PUT /users/<id>` - Update user
- `DELETE /users/<id>` - Delete user
- `GET|POST /roles` - Manage roles
- `GET /analytics/products` - Product analytics
- `GET /orders` - View all customer orders
- `GET /analytics/dashboard` - Admin dashboard data

## 🔒 Security Features

- JWT-based authentication
- Password hashing (Werkzeug)
- Role-based access control
- Protected admin routes
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Environment variable protection

## 🧪 Testing Strategy

- Unit tests for all models
- Integration tests for API endpoints
- Authentication flow testing
- Cart and checkout logic testing
- Analytics query validation
- Test coverage target: 80%+

## 📝 Development Workflow

1. Each team member works on assigned files
2. Create feature branches for development
3. Write tests before implementation (TDD)
4. Ensure all tests pass before committing
5. Submit pull requests for code review
6. Merge to main after approval

## 🎨 Design Guidelines

- Mobile-first responsive design
- Consistent color scheme and typography
- Intuitive navigation and user flows
- Accessible UI components (WCAG compliance)
- Fast loading times and optimized images
- Clear call-to-action buttons

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

## 🤝 Contributing

Each team member should:
1. Follow the coding standards and style guide
2. Write comprehensive tests for new features
3. Document API endpoints and functions
4. Keep commits atomic and descriptive
5. Communicate blockers and dependencies

## 📄 License

This project is developed as part of a team assignment.

---

**Project Status**: In Development  
**Last Updated**: 2024  
**Team**: Banai, Kabathi, Sharon, Amos, Edward