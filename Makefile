# Makefile for Stockport v4

.PHONY: help test test-unit test-integration test-coverage test-all clean install lint format

help:
	@echo "Stockport v4 - Available Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo "  make test-all         - Run all tests with full coverage"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean generated files"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock black flake8 mypy

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-coverage:
	pytest tests/ --cov=backend --cov=ui --cov=models --cov-report=html --cov-report=term-missing

test-all:
	pytest tests/ -v --cov=backend --cov=ui --cov=models --cov-report=html --cov-report=term-missing --cov-report=xml --cov-fail-under=70

lint:
	flake8 backend/ ui/ models/ --max-line-length=100 --exclude=__pycache__,*.pyc
	mypy backend/ ui/ models/ --ignore-missing-imports

format:
	black backend/ ui/ models/ tests/ --line-length=100

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf coverage.xml
	rm -rf .mypy_cache

