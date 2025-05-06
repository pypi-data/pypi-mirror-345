.PHONY: setup dev install clean format lint test

setup:
	pip install -U uv
	uv venv

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

clean:
	rm -rf .venv
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build

format:
	uv pip install black isort
	uv run black .
	uv run isort .

lint:
	uv pip install ruff mypy
	uv run ruff check .
	uv run mypy .

test:
	uv pip install pytest
	uv run pytest

all: clean setup install dev 