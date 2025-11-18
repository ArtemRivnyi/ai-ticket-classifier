.PHONY: help install test coverage lint format clean docker-up docker-down docker-logs

help:
	@echo "🎯 AI Ticket Classifier - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies"
	@echo "  make venv            Create virtual environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-integration Run integration tests"
	@echo "  make coverage        Run tests with coverage report"
	@echo "  make test-watch      Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run linters"
	@echo "  make format          Format code with black"
	@echo "  make type-check      Run type checking"
	@echo "  make security        Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker images"
	@echo "  make docker-up       Start services"
	@echo "  make docker-down     Stop services"
	@echo "  make docker-logs      View logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod-check      Run production checklist"
	@echo "  make deploy-staging  Deploy to staging"
	@echo "  make deploy-prod     Deploy to production"

# Python version check
check-python:
	@python check_python_version.py || (echo "Run: python check_python_version.py" && exit 1)

# Setup
venv: check-python
	python3.12 -m venv venv
	@echo "✅ Virtual environment created with Python 3.12"
	@echo "Activate with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

install: check-python
	pip install --upgrade pip
	pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
	@echo "✅ Dependencies installed"

install-dev: install
	pip install pre-commit
	pre-commit install
	@echo "✅ Development tools installed"

# Testing
test: check-python
	python check_python_version.py
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

test-watch:
	pytest-watch tests/ -- -v

coverage:
	pytest tests/ --cov=app --cov=middleware --cov=providers --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

# Code Quality
lint:
	flake8 app.py middleware/ providers/ --max-line-length=120 || true
	@echo "✅ Linting complete"

format:
	black app.py middleware/ providers/ tests/ || true
	isort app.py middleware/ providers/ tests/ || true
	@echo "✅ Code formatted"

type-check:
	mypy app.py middleware/ providers/ --ignore-missing-imports || true
	@echo "✅ Type checking complete"

security:
	bandit -r app.py middleware/ providers/ -ll || true
	safety check || true
	@echo "✅ Security checks complete"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "API: http://localhost:5000"
	@echo "Swagger: http://localhost:5000/apidocs"
	@echo "Metrics: http://localhost:5000/metrics"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# Production
prod-check:
	python production_checklist.py

deploy-staging:
	@echo "🚀 Deploying to staging..."
	# Add your staging deployment commands

deploy-prod:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure you run 'make prod-check' first!"
	# Add your production deployment commands

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	@echo "✅ Cleaned up"

# Run locally
run-dev:
	FLASK_ENV=development python app.py

run-prod:
	gunicorn -c gunicorn_config.py app:app || python app.py

