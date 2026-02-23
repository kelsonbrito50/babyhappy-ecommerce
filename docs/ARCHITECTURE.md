# Architecture Overview

## Tech Stack

- **Backend:** Django 4.x
- **Database:** PostgreSQL
- **Cache:** Redis
- **Web Server:** Nginx
- **Container:** Docker + Docker Compose

## Structure

```
apps/
├── products/    # Product catalog
├── orders/      # Order management
├── cart/        # Shopping cart
└── users/       # User auth
config/
├── settings.py  # Django settings
└── urls.py      # URL routing
```
