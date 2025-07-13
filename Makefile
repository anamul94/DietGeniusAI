# Variables
APP_NAME := fastapi-app
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "v1.0.0")
IMAGE_TAG := $(APP_NAME):$(VERSION)
IMAGE_LATEST := $(APP_NAME):latest
CONTAINER_NAME := $(APP_NAME)-container

.PHONY: help install dev test lint format clean build up down logs shell migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn app.main:app --reload --host localhost --port 8000
stop-dev: ## Stop development server
	pkill -f "uvicorn app.main:app"

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-auth: ## Run auth tests only
	pytest tests/test_auth.py -v

test-users: ## Run user tests only
	pytest tests/test_users.py -v

lint: ## Run linting
	flake8 app/
	black --check app/

format: ## Format code
	black app/
	isort app/

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

build: ## Build Docker image with version tag
	docker build -t $(IMAGE_TAG) -t $(IMAGE_LATEST) .
	@echo "Built image: $(IMAGE_TAG)"

run: ## Run container with name and restart policy
	docker run -d --name $(CONTAINER_NAME) --restart unless-stopped -p 8000:8000 $(IMAGE_LATEST)
	@echo "Started container: $(CONTAINER_NAME)"

stop: ## Stop named container
	docker stop $(CONTAINER_NAME)

remove: ## Remove named container
	docker rm $(CONTAINER_NAME)

restart: stop remove run ## Restart container

version: ## Show current version
	@echo "Version: $(VERSION)"
	@echo "Image: $(IMAGE_TAG)"

build-compose: ## Build with docker-compose
	docker-compose build

up: ## Start services with docker-compose
	docker-compose up -d

down: ## Stop services with docker-compose
	docker-compose down

logs: ## View logs
	docker-compose logs -f

shell: ## Access app container shell
	docker-compose exec app bash

db-shell: ## Access database shell
	docker-compose exec db psql -U postgres -d fastapi_db

migrate: ## Run database migrations
	docker-compose exec app alembic upgrade head

migrate-local: ## Run database migrations locally
	.venv/bin/alembic upgrade head

migration: ## Create new migration (usage: make migration msg="your message")
	.venv/bin/alembic revision --autogenerate -m "$(msg)"

migration-manual: ## Create empty migration file (usage: make migration-manual msg="your message")
	.venv/bin/alembic revision -m "$(msg)"

downgrade: ## Downgrade database by one revision
	.venv/bin/alembic downgrade -1

db-history: ## Show migration history
	.venv/bin/alembic history

db-current: ## Show current migration
	.venv/bin/alembic current

init-db: ## Initialize database
	python init_db.py

create-admin: ## Create admin user
	python create_admin.py