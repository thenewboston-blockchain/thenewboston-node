.PHONY: build
build:
	docker build . -t thenewboston-node:current

.PHONY: test
test:
	# We do not provide `THENEWBOSTON_NODE_TEST_WITH_ENV_VARS` to avoid mess up with local
    # dev env environment variables and provide reproducible test runs.
	PYTEST_RUN_SLOW_TESTS=true THENEWBOSTON_NODE_LOGGING='{"loggers":{"thenewboston_node":{"level":"WARNING"}}}' poetry run pytest -v -rs -n auto --cov=thenewboston_node --cov-report=html --show-capture=no

.PHONY: test-dockerized
test-dockerized:
	docker-compose build node  # to force rebuild the image for new changes
	docker-compose run -e THENEWBOSTON_NODE_TEST_WITH_ENV_VARS=true node pytest -v -rs -n auto

.PHONY: up-dependencies-only
up-dependencies-only:
	docker-compose up --force-recreate db

.PHONY: up
up:
	docker-compose up --force-recreate --build

.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	poetry run python -m thenewboston_node.manage migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: update
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

.PHONY: lint-and-test
lint-and-test: lint test ;

docs:
	mkdir -p docs

.PHONY: docs-rst
docs-rst: docs
	poetry run python -m thenewboston_node.manage generate_documentation > docs/thenewboston-blockchain-format.rst

.PHONY: docs-html
docs-html: docs
	poetry run python -m thenewboston_node.manage generate_documentation | poetry run rst2html.py > docs/thenewboston-blockchain-format.html

.PHONY: docs-html-test
docs-html-test:
	poetry run python -m thenewboston_node.manage generate_documentation | poetry run rst2html.py --strict > /dev/null
