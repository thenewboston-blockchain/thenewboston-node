#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=docker.pkg.github.com

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"
CLEAR_BLOCKCHAIN="${CLEAR_BLOCKCHAIN:-$3}"
CLEAR_BLOCKCHAIN="${CLEAR_BLOCKCHAIN:-False}"
INITIALIZE_FROM_ALPHA="${INITIALIZE_FROM_ALPHA:-$4}"
INITIALIZE_FROM_ALPHA="${INITIALIZE_FROM_ALPHA:-False}"

docker logout docker.pkg.github.com

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

test -f .env || touch .env
grep -q -o THENEWBOSTON_NODE_SECRET_KEY .env || echo "THENEWBOSTON_NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)" >> .env

docker-compose pull

grep -q -o THENEWBOSTON_NODE_NODE_SIGNING_KEY .env || echo "THENEWBOSTON_NODE_NODE_SIGNING_KEY=$(docker-compose --log-level CRITICAL run --rm node poetry run python -m thenewboston_node.manage generate_signing_key)" >> .env

if [ "$CLEAR_BLOCKCHAIN" == True ]; then
  echo "Clearing blockchain..."
  docker-compose run --rm node poetry run python -m thenewboston_node.manage clear_blockchain
fi

echo "Running migrations..."
docker-compose run --rm node poetry run python -m thenewboston_node.manage migrate
echo "Initializing blockchain..."
if [ "$INITIALIZE_FROM_ALPHA" == True ]; then
  docker-compose run --rm node bash 'poetry run python -m thenewboston_node.manage initialize_blockchain ${ARF_URL} ${ARF_PATH}'
else
  docker-compose run --rm node bash 'poetry run python -m thenewboston_node.manage initialize_blockchain ${BLOCKCHAIN_STATE_PATH}'
fi


docker-compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

counter=0
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8555/api/v1/nodes/self/); do
    counter=$(($counter + 1))
    if [ ${counter} -ge 12 ];then
      echo 'Unable to start node'
      exit 1
    fi

    echo "Node has not started yet, waiting 5 seconds for retry (${counter})"
    sleep 5
done

echo 'Node is up and running'
