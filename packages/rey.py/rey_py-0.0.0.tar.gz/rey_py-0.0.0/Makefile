# Makefile for helping with repetitive development tasks

.PHONY: clean clean-pyc clean-build docs help install-dev lint format test test-all init init-git mypy
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  init       - install package in development mode and initialize git repo"
	@echo "  init-git   - initialize git repository and set up pre-commit hooks"
	@echo "  clean      - remove all build, test, coverage and Python artifacts"
	@echo "  clean-pyc  - remove Python file artifacts"
	@echo "  clean-build - remove build artifacts"
	@echo "  install-dev - install the package in development mode"
	@echo "  lint       - check style with ruff"
	@echo "  format     - format code with ruff"

	@echo "  mypy       - run type checking with mypy"

	@echo "  test       - run tests quickly with pytest"
	@echo "  test-all   - run tests on various Python versions with nox"
	@echo "  coverage   - check code coverage quickly with pytest"
	@echo "  docs       - generate Sphinx HTML documentation"
	@echo "  build      - build wheel package"
	@echo "  release    - package and upload a release"

# Complete project initialization: install dependencies and initialize git
init: init-git install-dev init-pre-commit
	@echo "🎉 Project successfully set up with dependencies and git! Happy coding! 🚀"

# Initialize git repository and set up pre-commit hooks
init-git:
	@echo "Initializing git repository..."
	git init
	@echo "✓ Git repository initialized"
init-pre-commit:
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

clean: clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.ruff_cache' -exec rm -fr {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr .eggs/
	rm -fr .nox/

install-dev:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .


mypy:
	@echo "Running type checking with mypy..."
	mypy --config-file=pyproject.toml rey


test:
	pytest

test-all:
	nox -s tests

coverage:
	pytest --cov=rey --cov-report=term --cov-report=html
	@echo "Open htmlcov/index.html to see the coverage report."

docs:
	sphinx-build -b html docs docs/_build/html
	@echo "Open docs/_build/html/index.html to see the documentation."

build: clean
	pip install build
	python -m build

release: build
	pip install twine
	twine check dist/*
	@echo "Ready to release. Run the following command to upload to PyPI:"
	@echo "twine upload dist/*"
