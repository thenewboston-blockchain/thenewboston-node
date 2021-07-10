#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=docker.pkg.github.com
START_NODE_ARGS="${START_NODE_ARGS:-$1}"
GITHUB_USERNAME="${GITHUB_USERNAME:-$2}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$3}"

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  echo "Interactive docker registry login (username=github username; password=github personal access token (not github password)"
  docker login $DOCKER_REGISTRY_HOST
else
  echo "Automated docker registry login"
  # TODO(dmu) LOW: Implement a defensive technique to avoid printing password in case of `set -x`
  docker login --username "$GITHUB_USERNAME" --password "$GITHUB_PASSWORD" $DOCKER_REGISTRY_HOST
fi

wget https://raw.githubusercontent.com/thenewboston-developers/thenewboston-node/master/docker-compose.yml -O docker-compose.yml

grep -o THENEWBOSTON_NODE_SECRET_KEY .env || echo "THENEWBOSTON_NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)" >> .env
grep -o THENEWBOSTON_NODE_NODE_SIGNING_KEY .env || echo "THENEWBOSTON_NODE_NODE_SIGNING_KEY=$(docker-compose run --rm node poetry run python -m thenewboston_node.manage generate_signing_key)" >> .env
grep -o START_NODE_ARGS .env && sed -i "s/START_NODE_ARGS=.*/START_NODE_ARGS=${START_NODE_ARGS}/" .env || echo "START_NODE_ARGS=${START_NODE_ARGS}" >> .env

docker-compose pull
docker-compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST
