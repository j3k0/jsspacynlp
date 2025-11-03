.PHONY: help install build test clean docker-build docker-up docker-down docs

help:
	@echo "jsspacynlp - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install all dependencies"
	@echo "  make build         Build client library"
	@echo "  make test          Run all tests"
	@echo "  make test-server   Run server tests"
	@echo "  make test-client   Run client tests"
	@echo "  make lint          Lint all code"
	@echo "  make format        Format all code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  Build Docker images"
	@echo "  make docker-up     Start services"
	@echo "  make docker-down   Stop services"
	@echo "  make docker-logs   View logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove build artifacts"

install:
	@echo "Installing Python dependencies..."
	cd server && pip install -r requirements-dev.txt
	@echo "Installing Node.js dependencies..."
	cd client && npm install
	@echo "Installation complete!"

build:
	@echo "Building client library..."
	cd client && npm run build
	@echo "Build complete!"

test:
	@echo "Running server tests..."
	cd server && pytest
	@echo "Running client tests..."
	cd client && npm test
	@echo "All tests passed!"

test-server:
	@echo "Running server tests..."
	cd server && pytest

test-client:
	@echo "Running client tests..."
	cd client && npm test

test-integration:
	@echo "Running integration tests..."
	cd server && pytest -m integration

lint:
	@echo "Linting server code..."
	cd server && ruff check app/ tests/
	@echo "Linting client code..."
	cd client && npm run lint

format:
	@echo "Formatting server code..."
	cd server && black app/ tests/
	@echo "Formatting client code..."
	cd client && npm run format

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	@echo "Cleaning build artifacts..."
	rm -rf client/dist/
	rm -rf client/node_modules/
	rm -rf server/__pycache__/
	rm -rf server/app/__pycache__/
	rm -rf server/tests/__pycache__/
	rm -rf server/.pytest_cache/
	rm -rf server/htmlcov/
	rm -rf server/.coverage
	@echo "Clean complete!"

