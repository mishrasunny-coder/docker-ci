# Page Tracker Application Makefile
# This Makefile provides convenient commands for development and testing

.PHONY: help up down build test-unit test-integration test-e2e test-all lint black isort pylint bandit format check clean logs

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Service Management
up: ## Start all services (web + redis)
	@echo "🚀 Starting Page Tracker services..."
	docker compose up --build -d
	@echo "✅ Services started! Visit http://localhost:80"

down: ## Stop all services
	@echo "🛑 Stopping Page Tracker services..."
	docker compose down
	@echo "✅ Services stopped"

build: ## Build Docker images
	@echo "🔨 Building Docker images..."
	docker compose build

logs: ## Show service logs
	@echo "📋 Showing service logs..."
	docker compose logs -f

# Testing Commands
test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	cd web && source venv/bin/activate && python -m pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	cd web && source venv/bin/activate && python -m pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "🌐 Running end-to-end tests..."
	docker compose --profile testing up --build --exit-code-from test-service

test-all: ## Run all tests (unit + integration + e2e)
	@echo "🎯 Running all tests..."
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) test-e2e

# Code Quality Commands
lint: ## Run flake8 linting
	@echo "🔍 Running flake8 linting..."
	cd web && source venv/bin/activate && python -m flake8 src/

black: ## Format code with black
	@echo "🎨 Formatting code with black..."
	cd web && source venv/bin/activate && python -m black src/ tests/

isort: ## Sort imports with isort
	@echo "📦 Sorting imports with isort..."
	cd web && source venv/bin/activate && python -m isort src/ tests/

pylint: ## Run pylint analysis
	@echo "🔬 Running pylint analysis..."
	cd web && source venv/bin/activate && python -m pylint src/ --disable=C0114,C0116,R1705

bandit: ## Run security analysis with bandit
	@echo "🔒 Running security analysis with bandit..."
	cd web && source venv/bin/activate && python -m bandit -r src/ --quiet

format: black isort ## Format code (black + isort)

check: lint pylint bandit ## Run all code quality checks

# Development Commands
dev-setup: ## Set up development environment
	@echo "⚙️ Setting up development environment..."
	cd web && python3 -m venv venv
	cd web && source venv/bin/activate && pip install --upgrade pip
	cd web && source venv/bin/activate && pip install -e ".[dev]"

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down -v
	docker system prune -f

# CI/CD Commands
ci-test: ## Run tests as they would run in CI
	@echo "🔄 Running CI-style tests..."
	docker compose --profile testing up --build --exit-code-from test-service

# Quick Development Workflow
dev: up logs ## Start services and show logs

restart: down up ## Restart all services

# Status Commands
status: ## Show service status
	@echo "📊 Service Status:"
	docker compose ps

# Health Check
health: ## Check if services are healthy
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:80 > /dev/null && echo "✅ Web service is healthy" || echo "❌ Web service is not responding"
