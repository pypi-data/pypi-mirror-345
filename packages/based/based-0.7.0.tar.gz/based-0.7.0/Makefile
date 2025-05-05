.PHONY: help bootstrap lint test build clean
DEFAULT: help

VENV = .venv
PYTHON = $(VENV)/bin/python

help:
	@echo "Available targets:"
	@echo "  bootstrap - setup development environment"
	@echo "  lint      - run static code analysis"
	@echo "  test      - run project tests"
	@echo "  build     - build packages"
	@echo "  clean     - clean environment and remove development artifacts"

bootstrap:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip==24.2 setuptools==75.2.0 wheel==0.44.0 build==1.2.2.post1
	$(PYTHON) -m pip install -e .[postgres,sqlite,mysql,dev]

lint: $(VENV)
	$(PYTHON) -m ruff check based tests

test: $(VENV)
	$(PYTHON) -m pytest

build: $(VENV)
	$(PYTHON) -m build

clean:
	rm -rf $(VENV) .coverage .mypy_cache .pytest_cache .ruff_cache htmlcov based.egg-info coverage.xml build dist
	find . -type d -name "__pycache__" | xargs rm -rf
