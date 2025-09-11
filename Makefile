# LegalEase AI Development Makefile

.PHONY: help setup build up down logs clean test lint format

# Default target
help:
	@echo "LegalEase AI Development Commands:"
	@echo "  setup     - Initial project setup"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - View logs from all services"
	@echo "  clean     - Clean up Docker resources"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"

# Initial project setup
setup:
	@echo "Setting up LegalEase AI development environment..."
	@cp .env.example .env
	@echo "Created .env file from template"
	@echo "Please update .env with your API keys and configuration"
	@docker-compose build
	@echo "Setup complete! Run 'make up' to start services"

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build

# Start all services
up:
	@echo "Starting LegalEase AI services..."
	@docker-compose up -d
	@echo "Services started. Access:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  RabbitMQ Management: http://localhost:15672"

# Start services with logs
up-logs:
	@echo "Starting services with logs..."
	@docker-compose up

# Stop all services
down:
	@echo "Stopping LegalEase AI services..."
	@docker-compose down

# View logs
logs:
	@docker-compose logs -f

# View logs for specific service
logs-backend:
	@docker-compose logs -f backend

logs-frontend:
	@docker-compose logs -f frontend

logs-postgres:
	@docker-compose logs -f postgres

logs-redis:
	@docker-compose logs -f redis

logs-rabbitmq:
	@docker-compose logs -f rabbitmq

# Clean up Docker resources
clean:
	@echo "Cleaning up Docker resources..."
	@docker-compose down -v
	@docker system prune -f
	@docker volume prune -f

# Development commands
dev-backend:
	@echo "Starting backend in development mode..."
	@cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	@cd frontend && npm run dev

# Database commands
db-migrate:
	@echo "Running database migrations..."
	@docker-compose exec backend alembic upgrade head

db-revision:
	@echo "Creating new database revision..."
	@docker-compose exec backend alembic revision --autogenerate -m "$(message)"

db-reset:
	@echo "Resetting database..."
	@docker-compose down postgres
	@docker volume rm legalease-ai_postgres_data
	@docker-compose up -d postgres
	@sleep 10
	@make db-migrate

# Testing
test:
	@echo "Running all tests..."
	@docker-compose exec backend pytest
	@cd frontend && npm test

test-backend:
	@echo "Running backend tests..."
	@docker-compose exec backend pytest

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm test

# Code quality
lint:
	@echo "Running linting..."
	@docker-compose exec backend black --check .
	@docker-compose exec backend isort --check-only .
	@docker-compose exec backend mypy .
	@cd frontend && npm run lint

format:
	@echo "Formatting code..."
	@docker-compose exec backend black .
	@docker-compose exec backend isort .
	@cd frontend && npm run lint --fix

# Install dependencies
install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@curl -f http://localhost:3000 || echo "Frontend not responding"

# Backup and restore
backup-db:
	@echo "Creating database backup..."
	@docker-compose exec postgres pg_dump -U legalease_user legalease_ai > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	@echo "Restoring database from backup..."
	@docker-compose exec -T postgres psql -U legalease_user legalease_ai < $(file)