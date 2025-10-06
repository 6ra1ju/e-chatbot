# Django E-commerce API Server

Django REST API server for the e-commerce application.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create superuser (optional):**
```bash
python manage.py createsuperuser
```

4. **Populate sample data:**
```bash
python manage.py populate_products
```

5. **Run server:**
```bash
python manage.py runserver
```

## API Endpoints

- `GET /api/products/` - Get all products
- `GET /api/products/{id}/` - Get specific product
- `POST /api/products/create/` - Create new product

## Admin Interface

Access Django admin at: `http://localhost:8000/admin/`

## Database

Uses SQLite3 database (`db.sqlite3`) with the following models:

### Product Model
- `name` - Product name
- `price` - Current price
- `original_price` - Original price (optional)
- `discount` - Discount percentage (optional)
- `rating` - Product rating (optional)
- `sold_count` - Number of items sold (optional)
- `image` - Product image URL (optional)
- `labels` - JSON array of labels (optional)

## Development

The server includes:
- Django REST Framework for API
- CORS headers for frontend integration
- Admin interface for data management
- Management commands for data population 