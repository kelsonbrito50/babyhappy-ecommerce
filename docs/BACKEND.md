# Backend Development Guide

## Stack

- **Framework:** Django 4.x
- **Database:** PostgreSQL
- **Payments:** Cielo (Brazilian credit card processor)
- **CDN/Security:** Cloudflare WAF
- **Container:** Docker

## App Structure

```
apps/
├── products/     # Product catalog, baby item categories
├── orders/       # Order management and tracking
├── cart/         # Shopping cart
├── users/        # Customer accounts
└── payments/     # Cielo payment integration
config/
├── settings.py   # Django configuration
└── urls.py       # URL routing
```

## Running Locally

```bash
docker-compose up --build
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Payment Integration

This project uses Cielo for payment processing:

```python
# Sandbox credentials in .env
CIELO_MERCHANT_ID=...
CIELO_MERCHANT_KEY=...
CIELO_SANDBOX=True
```

Never use production credentials in development!

## Static Files

```bash
python manage.py collectstatic
```

Static files are served via Cloudflare CDN in production.
