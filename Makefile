.PHONY: build
build: build-node build-reverse-proxy ;

.PHONY: build-node
build-node:
	docker build . --build-arg RESET_DOCKER_CACHE="$$(date)" --target=node -t thenewboston-node:current

.PHONY: build-reverse-proxy
build-reverse-proxy:
	docker build . --target=reverse-proxy -t thenewboston-node-reverse-proxy:current

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
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate db

.PHONY: up
up: build-node build-reverse-proxy
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate

.PHONY: up-prod
up-prod: build-node build-reverse-proxy
	docker-compose up --force-recreate

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

.PHONY: generate-signing-key
generate-signing-key:
	poetry run python -m thenewboston_node.manage generate_signing_key

.PHONY: generate-blockchain
generate-blockchain:
	mkdir -p local/blockchain
	poetry run python -m thenewboston_node.manage generate_blockchain -f --path local/blockchain --do-not-validate 220 > local/blockchain-generation.log 2>&1

.PHONY: run-server
run-server:
	poetry run python -m thenewboston_node.manage runserver 127.0.0.1:8555

.PHONY: dev-initialize-blockchain
dev-initialize-blockchain:
	poetry run python -m thenewboston_node.manage initialize_blockchain -f https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json

.PHONY: dev-download-latest-blockchain-state
dev-download-latest-blockchain-state:
	poetry run python -m thenewboston_node.manage download_latest_blockchain_state http://3.143.205.184:8555/

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: lint-and-test
lint-and-test: lint test ;

docs:
	mkdir -p docs

.PHONY: docs-rst
docs-rst: docs
	THENEWBOSTON_NODE_SECRET_KEY=default poetry run python -m thenewboston_node.manage generate_documentation > docs/thenewboston-blockchain-format.rst

.PHONY: docs-html
docs-html: docs
	THENEWBOSTON_NODE_SECRET_KEY=default poetry run python -m thenewboston_node.manage generate_documentation | poetry run rst2html.py > docs/thenewboston-blockchain-format.html

.PHONY: docs-html-test
docs-html-test: SHELL:=/bin/bash
docs-html-test:
	set -o pipefail && THENEWBOSTON_NODE_SECRET_KEY=default poetry run python -m thenewboston_node.manage generate_documentation | poetry run rst2html.py --strict > /dev/null
