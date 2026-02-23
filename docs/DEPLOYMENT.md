# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 15+
- Python 3.11+

## Environment Setup

```bash
cp .env.example .env
# Edit .env with your production values
```

## Local Development

```bash
docker-compose up --build
```

App available at http://localhost:8000

## Production Deployment

### Using Docker Compose

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Database Migrations

Always run after deploying schema changes:
```bash
python manage.py migrate
```

## Payment Configuration

Configure Cielo credentials in `.env`:
```
CIELO_MERCHANT_ID=your-merchant-id
CIELO_MERCHANT_KEY=your-merchant-key
CIELO_SANDBOX=false  # true for testing
```
