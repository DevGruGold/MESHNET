# Contributing to MESHNET

Thank you for your interest in contributing to MESHNET! This document provides guidelines for contributors.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/MESHNET.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 🔧 Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linting
flake8 .
black --check .
isort --check-only .
```

## 📝 Code Style

- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters
- Use type hints where appropriate

## 🧪 Testing

- Use pytest for testing
- Aim for >80% code coverage
- Write unit tests for all functions
- Include integration tests for complex workflows
- Use fixtures for test data

## 📋 Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Submit your pull request with a clear description

## 🐛 Bug Reports

Please use the GitHub issue tracker to report bugs. Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 💡 Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Provide clear use case description
- Explain why this feature would benefit the project

## 🤝 Code of Conduct

Please be respectful and professional in all interactions.
