.PHONY: help install dev test coverage lint format migrate shell clean build deploy check

# ── Config ───────────────────────────────────────────────────────────────────

PYTHON       := python3
PIP          := pip
PYTEST       := python3 -m pytest
SETTINGS_DEV := config.settings.development
SETTINGS_TEST:= config.settings.test
MANAGE       := DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) $(PYTHON) manage.py
DOCKER       := docker compose

# ── Help ─────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────────

install: ## Install production dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development + test dependencies
	$(PIP) install -r requirements-dev.txt

setup: install-dev migrate ## Full local setup (install + migrate)

env: ## Copy .env.example to .env (safe — won't overwrite existing)
	@test -f .env || (cp .env.example .env && echo ".env created from .env.example")

# ── Docker ───────────────────────────────────────────────────────────────────

dev: ## Start all services with Docker Compose (attach)
	$(DOCKER) up

dev-d: ## Start all services with Docker Compose (detach)
	$(DOCKER) up -d

down: ## Stop Docker Compose services
	$(DOCKER) down

build: ## Build Docker images
	$(DOCKER) build

build-prod: ## Build production Docker image
	docker build --target production -t babyhappy-ecommerce:latest .

logs: ## Follow Docker Compose logs
	$(DOCKER) logs -f

# ── Database ─────────────────────────────────────────────────────────────────

migrate: ## Apply database migrations
	$(MANAGE) migrate

makemigrations: ## Create new migrations
	$(MANAGE) makemigrations

migrate-test: ## Run migrations on the test database (SQLite in-memory)
	DJANGO_SETTINGS_MODULE=$(SETTINGS_TEST) $(PYTHON) manage.py migrate

createsuperuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

# ── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all tests (fast, no coverage)
	$(PYTEST) apps/ -q

test-v: ## Run all tests with verbose output
	$(PYTEST) apps/ -v

coverage: ## Run tests with coverage report
	$(PYTEST) apps/ --cov=apps --cov-report=term-missing --cov-report=html --cov-fail-under=85

coverage-xml: ## Generate XML coverage report (for CI)
	$(PYTEST) apps/ --cov=apps --cov-report=xml --cov-fail-under=85

test-app: ## Run tests for a specific app: make test-app APP=products
	$(PYTEST) apps/$(APP)/ -v

# ── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Run flake8 linter
	flake8 apps/ config/ --max-line-length=100 --exclude=migrations

lint-strict: ## Run flake8 with strict settings
	flake8 apps/ config/ --max-line-length=88 --exclude=migrations --select=E,W,F

format: ## Auto-format code with black + isort
	black apps/ config/ --line-length=100
	isort apps/ config/ --profile=black

format-check: ## Check formatting without modifying files
	black apps/ config/ --check --diff --line-length=100
	isort apps/ config/ --check-only --profile=black

check: ## Run Django system checks
	$(MANAGE) check

check-deploy: ## Run Django deployment checks
	DJANGO_SETTINGS_MODULE=$(SETTINGS_DEV) $(PYTHON) manage.py check --deploy 2>&1 || true

# ── Development ──────────────────────────────────────────────────────────────

shell: ## Open interactive Django shell
	$(MANAGE) shell

shell-plus: ## Open enhanced Django shell (requires django-extensions)
	$(MANAGE) shell_plus

runserver: ## Start development server on port 8000
	$(MANAGE) runserver 0.0.0.0:8000

schema: ## Generate OpenAPI schema to stdout
	$(MANAGE) spectacular --validate

static: ## Collect static files
	$(MANAGE) collectstatic --noinput

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
	find . -name ".coverage" -delete 2>/dev/null; true
	rm -rf htmlcov/ .pytest_cache/ 2>/dev/null; true

# ── Deploy ───────────────────────────────────────────────────────────────────

deploy: build-prod ## Deploy to production (requires Docker + docker compose)
	$(DOCKER) -f docker-compose.yml up -d --build
	$(DOCKER) exec web python manage.py migrate --settings=config.settings.production
	$(DOCKER) exec web python manage.py collectstatic --noinput --settings=config.settings.production
