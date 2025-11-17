# Contributing to AI Ticket Classifier

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/ai-ticket-classifier.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `python run_all_tests.py`
6. Commit your changes: `git commit -m "feat: your feature description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## 📋 Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🧪 Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run `python run_all_tests.py` before committing

## 📝 Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all functions
- Keep comments in English

## 🔒 Security

- Never commit API keys or secrets
- Use `.env` for sensitive data
- Update `.env.example` if adding new variables

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎉

