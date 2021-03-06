.PHONY: up-dependencies-only
up-dependencies-only:
	docker-compose up --force-recreate db

.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	poetry run python -m thenewboston_node.manage migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: dev-env-update
update: install migrate install-pre-commit ;

.PHONY: create-superuser
create-superuser:
	poetry run python -m thenewboston_node.manage createsuperuser

.PHONY: run-server
run-server:
	poetry run python -m thenewboston_node.manage runserver 127.0.0.1:8001

.PHONY: lint
lint:
	poetry run pre-commit run --all-files
