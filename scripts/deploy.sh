#!/usr/bin/env bash

set -e

GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"

wget https://raw.githubusercontent.com/thenewboston-developers/thenewboston-node/master/docker-compose.yml -O docker-compose.yml

if [ ! -f .env ]; then
  cat <<EOF > .env
THENEWBOSTON_NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)
EOF
fi

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  echo "Interactive docker login"
  docker login docker.pkg.github.com
else
  echo "Automated docker login"
  # TODO(dmu) LOW: Implement a defensive technique to avoid printing password in case of `set -x`
  docker login --username "$GITHUB_USERNAME" --password "$GITHUB_PASSWORD" docker.pkg.github.com
fi

docker-compose pull
docker-compose up -d --force-recreate
docker logout
