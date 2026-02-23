# Testing Guide

## Setup

```bash
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific app
pytest apps/products/tests/
```

## Test Organization

```
apps/
├── products/tests/
├── orders/tests/
├── cart/tests/
└── users/tests/
conftest.py   # Shared fixtures
```

## Writing Tests

```python
import pytest
from decimal import Decimal

@pytest.mark.django_db
def test_product_price(product):
    assert product.price > Decimal('0')

@pytest.mark.django_db  
def test_cart_add_item(authenticated_client):
    response = authenticated_client.post('/cart/add/', {
        'product_id': 1,
        'quantity': 2
    })
    assert response.status_code == 302
```

## Coverage Target

Aim for >80% on core business logic.
