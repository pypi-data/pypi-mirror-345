# Development Guide

## Setup

1. Clone the repository
2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Testing

### Unit Tests
```bash
pytest tests/unit
```

### Integration Tests
Requires running Vector Store server on http://localhost:8007

```bash
pytest tests/integration
```

### Code Style
```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
ruff check .
```

## Building Documentation
```bash
# Install documentation dependencies
pip install -r requirements/dev.txt

# Build documentation
sphinx-build -b html docs/source docs/build
```

## Release Process

1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Create release commit:
```bash
git commit -m "Release v0.1.0"
git tag v0.1.0
```

4. Build and upload to PyPI:
```bash
python -m build
python -m twine upload dist/*
```

## Project Structure

```
vector_store_client/           # Root directory
├── vector_store_client/       # Package source
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Main client implementation
│   ├── models.py             # Data models
│   ├── exceptions.py         # Custom exceptions
│   └── types.py              # Type definitions
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docs/                    # Documentation
├── examples/                # Usage examples
└── requirements/            # Dependencies
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request 