.PHONY: install dev test lint format migrate migrate-new docker-up docker-down superuser

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

lint:
	ruff check app tests
	ruff format --check app tests

format:
	ruff check --fix app tests
	ruff format app tests

migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(m)"

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

superuser:
	python -m scripts.create_superuser
