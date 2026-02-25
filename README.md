<!-- HERO -->
<div align="center">

# 🍼 BabyHappy E-Commerce Platform

### Production-grade Django e-commerce powering a real Brazilian baby products brand.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![CI](https://img.shields.io/github/actions/workflow/status/kelsonbrito50/babyhappy-ecommerce/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/kelsonbrito50/babyhappy-ecommerce/actions)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[🌐 Live Website](https://babyhappyjp.com.br)** · **[📖 API Docs](#api-endpoints)** · **[🚀 Quick Start](#quick-start)**

</div>

---

<!-- screenshot -->

---

## About

This isn't a tutorial project. BabyHappy is a **real Brazilian baby products company**, and this platform is what processes their orders and payments.

The production system handles real Cielo credit card transactions, real inventory, and real customers at [babyhappyjp.com.br](https://babyhappyjp.com.br). Everything here is what I built from scratch: the entire application layer, REST API, payment integration, and business logic. Sensitive production configs are excluded for security.

> **100% of the application code** was written by me. The infrastructure and DevOps layer was handled by Lucas Amarante.

---

## Tech Stack

| Category | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Framework** | Django 4.2 |
| **REST API** | Django REST Framework |
| **Database** | PostgreSQL 16 |
| **Cache / Queue** | Redis |
| **Containerization** | Docker + Docker Compose |
| **Web Server** | Nginx (reverse proxy) |
| **Payment Gateway** | Cielo (credit card processing) |
| **CI/CD** | GitHub Actions |
| **Security** | Cloudflare WAF, DDoS protection, SSL/TLS |

---

## Architecture

Four-container Docker setup, production-parity from day one:

```
┌─────────────────────────────────────────────┐
│                  Cloudflare                 │
│           WAF · DDoS · SSL/TLS             │
└────────────────────┬────────────────────────┘
                     │
              ┌──────▼──────┐
              │    nginx    │  ← reverse proxy, static files
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │     web     │  ← Django / Gunicorn (app server)
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │                       │
  ┌──────▼──────┐       ┌────────▼────────┐
  │     db      │       │      redis       │
  │ PostgreSQL  │       │  cache / queue   │
  └─────────────┘       └─────────────────┘
```

---

## Features

- 🛒 **Product catalog** — categories, filtering, stock management
- 🧺 **Shopping cart** — session-based, persists across login
- 💳 **Cielo payment integration** — credit card processing with tokenization
- 📦 **Order management** — full lifecycle from placement to fulfillment
- 🔌 **REST API** — DRF-powered, token auth, JSON responses
- 🔒 **Cloudflare WAF** — DDoS protection and edge security
- 🐳 **Fully containerized** — one command to spin up the entire stack
- ⚙️ **GitHub Actions CI** — lint, test, and build on every push
- 📧 **Order notifications** — automated email on status changes
- 🔐 **JWT authentication** — secure API access for all user endpoints

---

## Quick Start

**Prerequisites:** Docker and Docker Compose installed.

```bash
# 1. Clone the repo
git clone https://github.com/kelsonbrito50/babyhappy-ecommerce.git
cd babyhappy-ecommerce

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your credentials (see .env.example for all required vars)

# 3. Spin up all containers
docker-compose up --build

# 4. Apply migrations and load initial data
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata fixtures/initial_data.json

# 5. Create a superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

App will be available at **http://localhost:8000**
Admin panel at **http://localhost:8000/admin**

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for dev, `False` for prod |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CIELO_MERCHANT_ID` | Cielo merchant ID |
| `CIELO_MERCHANT_KEY` | Cielo merchant key |
| `EMAIL_HOST` | SMTP host for notifications |

---

## API Endpoints

All endpoints are prefixed with `/api/v1/`.

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register/` | Create new user account |
| `POST` | `/auth/login/` | Obtain JWT token pair |
| `POST` | `/auth/token/refresh/` | Refresh access token |

### Products
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products/` | List all products (paginated) |
| `GET` | `/products/{id}/` | Product detail |
| `GET` | `/products/categories/` | List product categories |
| `GET` | `/products/?category={slug}` | Filter by category |

### Cart
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/cart/` | Get current cart |
| `POST` | `/cart/items/` | Add item to cart |
| `PATCH` | `/cart/items/{id}/` | Update item quantity |
| `DELETE` | `/cart/items/{id}/` | Remove item from cart |

### Checkout & Orders
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/checkout/` | Process order + payment |
| `GET` | `/orders/` | List user's orders |
| `GET` | `/orders/{id}/` | Order detail + status |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/payments/charge/` | Initiate Cielo charge |
| `GET` | `/payments/{id}/status/` | Check payment status |
| `POST` | `/payments/webhook/` | Cielo callback handler |

---

## What I Learned

Building a payment-integrated e-commerce from scratch for a real client taught me things no course will:

**Payment gateway integration is never straightforward.** Cielo's sandbox behaves differently from production in subtle ways. I built a full abstraction layer around the gateway so the business logic never touches Cielo directly — swapping providers would be a one-file change.

**Docker is non-negotiable for environment parity.** The "works on my machine" problem disappeared the day I containerized everything. CI runs the same containers that production does.

**Database transactions are your safety net.** Order creation, payment charge, and stock deduction are wrapped in a single atomic transaction. If the payment fails, no inventory is touched. This took two failed edge cases to get right.

**Django signals are powerful but dangerous.** I used them for order notifications and learned quickly that uncaught exceptions in signals can silently corrupt your request cycle. Async tasks via Celery would be the right call at higher volume.

**Rate limiting before you need it.** Added Cloudflare rate limiting to the payment endpoint early. Not because we had an attack — because thinking about it after the fact is always worse.

**REST API design is a contract.** Once clients depend on an endpoint, you can't break it. Versioning from day one (`/api/v1/`) saved a painful migration when the checkout flow changed.

---

## Project Structure

```
babyhappy-ecommerce/
├── apps/
│   ├── accounts/       # User auth, profiles
│   ├── catalog/        # Products, categories
│   ├── cart/           # Shopping cart logic
│   ├── orders/         # Order management
│   └── payments/       # Cielo gateway integration
├── config/
│   ├── settings/       # base, dev, prod settings split
│   └── urls.py
├── docker/
│   ├── nginx/          # Nginx config
│   └── postgres/       # DB init scripts
├── docker-compose.yml
├── docker-compose.prod.yml
└── Makefile            # Convenience commands
```

---

## Running Tests

```bash
# Run the full test suite inside the web container
docker-compose exec web python manage.py test

# With coverage report
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
```

---

## CI/CD

GitHub Actions runs on every push and pull request:

1. **Lint** — flake8 + black formatting check
2. **Test** — full test suite against a PostgreSQL service container
3. **Build** — Docker image build verification

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the full pipeline.

---

## Credits

| Role | Person |
|---|---|
| Application Development | [Kelson Brito](https://github.com/kelsonbrito50) |
| DevOps & Infrastructure | Lucas Amarante |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built for **[BabyHappy](https://babyhappyjp.com.br)** — making baby product shopping seamless in Brazil. 🍼

</div>
