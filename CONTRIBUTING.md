# Contributing to Red Team AI

Thank you for your interest in contributing to Red Team AI! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/red-team-ai.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt`
5. Install development dependencies: `pip install pytest pytest-asyncio black flake8`

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters
- Use Black for formatting: `black .`

## Project Structure

- `agents/`: Independent agent modules
- `orchestrator/`: Experiment coordination logic
- `backend/`: FastAPI application
- `frontend/`: React application
- `shared/`: Common utilities and schemas

## Adding New Features

### Adding a New Agent

1. Create new directory under `agents/`
2. Implement agent class with required methods
3. Add tests in `tests/agents/`
4. Update documentation

### Adding a New Metric

1. Add metric calculation to `agents/judging_agent/metrics.py`
2. Update `ScoreMetrics` schema in `shared/schemas.py`
3. Add tests
4. Update API documentation

### Adding a New Attack Strategy

1. Add strategy definition to `agents/interrogator_agent/strategies.py`
2. Add to `AttackStrategy` enum in `shared/schemas.py`
3. Implement tactics and templates
4. Add tests

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation as needed
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## Pull Request Guidelines

- Clear description of changes
- Reference any related issues
- Include test results
- Update CHANGELOG.md if applicable
- Ensure CI passes

## Code Review Process

- At least one maintainer approval required
- All comments must be addressed
- CI must pass
- Documentation must be updated

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release tag
4. Build and test
5. Publish release

## Questions?

- Open an issue for bugs
- Use discussions for questions
- Check existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.