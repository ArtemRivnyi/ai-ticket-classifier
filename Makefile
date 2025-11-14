.PHONY: help install test run build deploy clean docker-up docker-down docker-logs lint format security

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run all tests
	python -m pytest tests/ test_app.py -v --cov=. --cov-report=html --cov-report=term

test-fast: ## Run tests without coverage
	python -m pytest tests/ test_app.py -v

run: ## Run application locally
	python app.py

run-prod: ## Run with gunicorn (production mode)
	gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d

docker-down: ## Stop Docker containers
	docker compose down

docker-logs: ## Show Docker logs
	docker compose logs -f

docker-restart: ## Restart Docker containers
	docker compose restart

docker-clean: ## Remove Docker containers and images
	docker compose down -v
	docker system prune -f

lint: ## Run code linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	pylint app.py classify.py

format: ## Format code with black
	black app.py classify.py test_app.py

security: ## Run security checks
	safety check
	bandit -r . -f json -o bandit-report.json

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "📝 Copy .env.example to .env and configure it"; \
		exit 1; \
	else \
		echo "✅ .env file exists"; \
	fi

setup: check-env install ## Initial setup (check env + install)
	@echo "✅ Setup complete!"

health-check: ## Check if service is running
	@curl -f http://localhost:5000/api/v1/health || echo "❌ Service is not running"

test-classify: ## Test classification endpoint
	@curl -X POST http://localhost:5000/api/v1/classify \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $${API_KEY}" \
		-d '{"ticket":"Cannot connect to VPN"}'

metrics: ## Show Prometheus metrics
	@curl http://localhost:5000/metrics

info: ## Show API info
	@curl http://localhost:5000/api/v1/info | python -m json.tool

logs: ## Show application logs
	@tail -f logs/app.log

clean: ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

all: clean install test docker-build ## Run complete build pipeline

production-check: ## Verify production readiness
	@echo "🔍 Checking production readiness..."
	@echo ""
	@echo "1. Environment configuration:"
	@make check-env
	@echo ""
	@echo "2. Running tests:"
	@make test-fast
	@echo ""
	@echo "3. Security scan:"
	@make security
	@echo ""
	@echo "4. Code quality:"
	@make lint
	@echo ""
	@echo "✅ Production readiness check complete!"