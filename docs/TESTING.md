# Testing Guide

## Run All Tests

```bash
python run_all_tests.py
```

## Run Specific Tests

```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov=middleware --cov=providers --cov=api --cov=security --cov-report=html
```

## Test Coverage

Current coverage: **80%**

View HTML report: `htmlcov/index.html`

