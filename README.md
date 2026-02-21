# 🍼 Baby Happy — E-Commerce Platform Demo

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.14-red?logo=django&logoColor=white)](https://django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Protected-F38020?logo=cloudflare&logoColor=white)](https://cloudflare.com)
[![Production](https://img.shields.io/badge/🔴_Live-babyhappyjp.com.br-success)](https://babyhappyjp.com.br)

> **Sanitized demo** of a production e-commerce platform built for a Brazilian baby products company.  
> The production version runs at [babyhappyjp.com.br](https://babyhappyjp.com.br) with real payment processing, inventory management, and customer accounts.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│  Django     │────▶│ PostgreSQL  │
│  (reverse   │     │  Gunicorn   │     │   16        │
│   proxy)    │     │  :8000      │     │  :5432      │
│  :80/:443   │     └──────┬──────┘     └─────────────┘
└─────────────┘            │
                           ▼
                    ┌─────────────┐
                    │   Redis     │
                    │  (cache +   │
                    │   sessions) │
                    │  :6379      │
                    └─────────────┘
```

**Request flow:** Client → Nginx (SSL termination, static files) → Gunicorn/Django → PostgreSQL/Redis

## ⚠️ Demo Notice

This repository is a **sanitized showcase** of the production system. Key differences:

- Payment gateway (Cielo) is **fully mocked** — no real transactions
- No real customer data or business logic
- Simplified configuration (no Cloudflare, Sentry, or monitoring integrations)
- Demo seed data only

## 🚀 Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/kelsonbrito50/babyhappy-ecommerce-demo.git
cd babyhappy-ecommerce-demo
cp .env.example .env
docker-compose up --build
```

The API will be available at `http://localhost/api/`.

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL and Redis credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products/` | List products (filters: `category`, `min_price`, `max_price`, `search`) |
| `GET` | `/api/products/{slug}/` | Product detail with images |
| `GET` | `/api/cart/` | View current cart |
| `POST` | `/api/cart/` | Add item to cart (`product_id`, `quantity`) |
| `POST` | `/api/orders/` | Create order from cart |
| `POST` | `/api/payments/cielo/authorize/` | Mock Cielo payment authorization |
| `POST` | `/api/payments/cielo/capture/` | Mock Cielo payment capture |

### Example: Browse Products

```bash
# List all products
curl http://localhost/api/products/

# Filter by category
curl http://localhost/api/products/?category=roupas

# Search
curl http://localhost/api/products/?search=body+bebe

# Price range
curl http://localhost/api/products/?min_price=20&max_price=100
```

### Example: Checkout Flow

```bash
# Add to cart
curl -X POST http://localhost/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# Create order
curl -X POST http://localhost/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Maria Silva", "email": "maria@example.com", "address": "Rua das Flores, 123"}'

# Authorize payment
curl -X POST http://localhost/api/payments/cielo/authorize/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "card_number": "4111111111111111", "expiry": "12/2028", "cvv": "123"}'

# Capture payment
curl -X POST http://localhost/api/payments/cielo/capture/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "CIELO-DEMO-xxxxx"}'
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Django 4.2, Django REST Framework |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 (sessions + caching) |
| **Web Server** | Nginx (reverse proxy + static files) |
| **Containers** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **Payments** | Cielo API (mocked in demo) |

## 💡 Skills Demonstrated

- **Full-stack Django development** with clean project architecture
- **RESTful API design** with filtering, pagination, and proper serialization
- **Payment gateway integration** (Cielo — Brazil's largest payment processor)
- **Docker containerization** with multi-service orchestration
- **PostgreSQL** data modeling with relationships and indexes
- **Redis** for session management and caching
- **Nginx** reverse proxy configuration with static file serving
- **CI/CD pipelines** with automated testing
- **Production deployment** patterns (environment separation, security headers)
- **Brazilian e-commerce** domain knowledge (Cielo, CPF validation, BRL currency)

## 📁 Project Structure

```
babyhappy-ecommerce-demo/
├── .github/workflows/ci.yml    # CI/CD pipeline
├── config/                     # Django project configuration
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Dev overrides
│   │   └── production.py      # Production settings
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI entry point
├── apps/
│   ├── accounts/              # Custom user (email-based auth)
│   ├── products/              # Product catalog + categories
│   ├── cart/                  # Session-based shopping cart
│   ├── orders/                # Order management
│   └── payments/              # Cielo payment mock
├── nginx/nginx.conf           # Nginx configuration
├── Dockerfile                 # Python app container
├── docker-compose.yml         # Multi-service orchestration
└── requirements.txt           # Python dependencies
```

## 👥 Production Team

This demo represents a real production system built collaboratively:

| Role | Contributor |
|------|-------------|
| Full Stack Development (Django, DRF, frontend, payments) | [Kelson Brito](https://github.com/kelsonbrito50) |
| DevOps & Infrastructure (Docker, Cloudflare, deployment) | [Lucas Amarante](https://github.com/lucasamarante27) |

---

## 📄 License

This demo is released under the MIT License. The production version at [babyhappyjp.com.br](https://babyhappyjp.com.br) is proprietary.

---

**Built by [Kelson Brito](https://github.com/kelsonbrito50)** 🇧🇷
