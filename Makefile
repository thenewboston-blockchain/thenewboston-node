.PHONY: install
install:
	poetry install

.PHONY: up-dependencies-only
up-dependencies-only:
	docker-compose up --force-recreate db

.PHONY: migrate
migrate:
	poetry run python -m thenewboston_node.manage migrate

.PHONY: create-superuser
create-superuser:
	poetry run python -m thenewboston_node.manage createsuperuser

.PHONY: run-server
run-server:
	poetry run python -m thenewboston_node.manage runserver 127.0.0.1:8001
