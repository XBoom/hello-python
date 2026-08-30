.PHONY: install dev test lint format migrate migrate-new docker-up docker-down superuser feature hotfix

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

# git-flow：从最新 develop 开一条任务分支
# 用法: make feature n=user-profile
feature:
	@test -n "$(n)" || (echo "用法: make feature n=<任务短名>"; exit 1)
	git fetch origin
	git checkout develop
	git pull --ff-only origin develop
	git checkout -b feature/$(n)

# git-flow：从最新 main 开热修分支
# 用法: make hotfix n=login-500
hotfix:
	@test -n "$(n)" || (echo "用法: make hotfix n=<问题短名>"; exit 1)
	git fetch origin
	git checkout main
	git pull --ff-only origin main
	git checkout -b hotfix/$(n)
