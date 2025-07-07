# Default target
default:
    @just --list

# Install dependencies
install:
    uv sync --extra dev

# Run all quality checks
check: lint typecheck test

# Lint code with ruff
lint:
    uv run ruff check .

# Format and fix code with ruff
fix:
    uv run ruff format .
    uv run ruff check . --fix

# Run type checking with mypy
typecheck:
    uv run mypy .

# Run all tests
test:
    uv run pytest

# Run unit tests only
test-unit:
    uv run pytest tests/unit/

# Run integration tests only
test-integration:
    uv run pytest tests/integration/

# Run e2e tests only
test-e2e:
    uv run pytest tests/e2e/

# Run tests with coverage
test-coverage:
    uv run pytest --cov=prompt_pidgeon --cov-report=html --cov-report=term

# Clean up generated files
clean:
    rm -rf .coverage
    rm -rf htmlcov/
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -name "*.pyc" -delete

# Development setup
dev-setup: install
    uv run pre-commit install

# Run the CLI in development mode
run *args:
    uv run python -m prompt_pidgeon.cli {{args}}

# Show project info
info:
    @echo "Project: prompt-pidgeon"
    @echo "Python version: $(cat .python-version)"
    @echo "Dependencies:"
    @uv tree 