# Crypto Streaming Pipeline - Makefile
# Run `make help` for a list of available commands.

.PHONY: help up down restart ps logs clean test lint fmt check psql tables build

# Default target: show help
help:
	@echo "Crypto Streaming Pipeline - Available commands:"
	@echo ""
	@echo "Stack management:"
	@echo "  make up          Start all services in detached mode"
	@echo "  make down        Stop all services"
	@echo "  make restart     Restart all services"
	@echo "  make ps          Show container status"
	@echo "  make logs        Tail logs from all services"
	@echo "  make logs SVC=x  Tail logs from one service (e.g. SVC=producer)"
	@echo "  make build       Rebuild images without starting"
	@echo "  make clean       Stop + remove volumes (DESTROYS DATA!)"
	@echo ""
	@echo "Dev workflow:"
	@echo "  make test        Run pytest suite"
	@echo "  make lint        Run ruff check"
	@echo "  make fmt         Auto-format code with ruff"
	@echo "  make check       Run lint + format check + test (mirrors CI)"
	@echo ""
	@echo "Database utilities:"
	@echo "  make psql        Connect to crypto_db as crypto_user"
	@echo "  make tables      List tables in crypto_db"

# Stack management
up:
	docker compose up -d
	@echo ""
	@echo "Stack started. Run 'make ps' to verify."

down:
	docker compose down

restart:
	docker compose restart

ps:
	docker compose ps

logs:
ifdef SVC
	docker compose logs -f --tail=100 $(SVC)
else
	docker compose logs -f --tail=50
endif

build:
	docker compose build

clean:
	@echo "WARNING: This will destroy all data volumes (Postgres, Caddy certs)."
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	docker compose down -v

# Dev workflow
test:
	pytest

lint:
	ruff check .

fmt:
	ruff format .
	ruff check --fix .

check:
	ruff check .
	ruff format --check .
	pytest

# Database utilities
psql:
	docker compose exec postgres psql -U crypto_user -d crypto_db

tables:
	docker compose exec postgres psql -U crypto_user -d crypto_db -c "\dt"
