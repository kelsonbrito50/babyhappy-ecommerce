# Developer Onboarding Guide

Welcome to BabyHappy E-commerce! Here's how to get started.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+

## Quick Start

```bash
git clone https://github.com/kelsonbrito50/babyhappy-ecommerce-demo.git
cd babyhappy-ecommerce-demo
cp .env.example .env
docker-compose up --build
```

## Initial Setup

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Visit http://localhost:8000/admin/ to set up products and categories.

## Key Configuration

### Payment (Cielo)

```bash
# .env (sandbox mode for development)
CIELO_MERCHANT_ID=your-sandbox-id
CIELO_MERCHANT_KEY=your-sandbox-key
CIELO_SANDBOX=True
```

Never use production Cielo credentials locally!

### Cloudflare

Cloudflare WAF rules are only active in production. Local dev bypasses them.

## Project Structure

```
apps/            # Django applications
config/          # Settings and URL configuration
nginx/           # Nginx configuration
docs/            # Project documentation
```

## Useful Commands

```bash
make dev         # Start all services
make test        # Run test suite
make migrate     # Apply migrations
make shell       # Django shell
```
