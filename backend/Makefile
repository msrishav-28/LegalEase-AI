# Makefile for LegalEase AI Backend

.PHONY: help install test test-unit test-integration test-performance test-security test-ai test-jurisdiction test-coverage clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e .[dev]

test: ## Run all tests
	python scripts/run_tests.py --type all --coverage

test-unit: ## Run unit tests
	python scripts/run_tests.py --type unit --verbose

test-integration: ## Run integration tests
	python scripts/run_tests.py --type integration --verbose

test-performance: ## Run performance tests
	python scripts/run_tests.py --type performance --verbose

test-security: ## Run security tests
	python scripts/run_tests.py --type security --verbose

test-ai: ## Run AI/ML accuracy tests
	python scripts/run_tests.py --type ai --verbose

test-jurisdiction: ## Run jurisdiction-specific tests
	python scripts/run_tests.py --jurisdiction --verbose

test-coverage: ## Run tests with coverage report
	python scripts/run_tests.py --type all --coverage --verbose

test-parallel: ## Run tests in parallel
	python scripts/run_tests.py --type all --parallel --coverage

lint: ## Run linting
	black --check .
	isort --check-only .
	mypy app/

format: ## Format code
	black .
	isort .

clean: ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test-quick: ## Run quick tests (unit only, no coverage)
	python scripts/run_tests.py --type unit

test-ci: ## Run tests for CI/CD
	python scripts/run_tests.py --type all --coverage --parallel