.PHONY: help test test-verbose lint format run docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make test          Run pytest suite"
	@echo "  make test-verbose  Run pytest suite with verbose output"
	@echo "  make lint          Run ruff check"
	@echo "  make format        Format code with ruff"
	@echo "  make run           Run API server locally via uvicorn"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start stack via docker compose"
	@echo "  make docker-down   Stop docker compose stack"
	@echo "  make clean         Remove build and cache artifacts"

test:
	pytest

test-verbose:
	pytest -v

lint:
	ruff check .

format:
	ruff format .

run:
	uvicorn main:mumble_rest --host 0.0.0.0 --port 2332 --reload

docker-build:
	docker build -t mumble-server-rest-api:latest .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

