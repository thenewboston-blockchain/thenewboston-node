#!/usr/bin/env bash

set -e
wget https://raw.githubusercontent.com/thenewboston-developers/thenewboston-node/master/docker-compose.yml -O docker-compose.yml

if [ ! -f .env ]; then
  cat <<EOF > .env
THENEWBOSTON_NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)
EOF
fi

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  docker login docker.pkg.github.com
else
  # Avoid printing the password
  { docker login -u $GITHUB_USERNAME -p $GITHUB_PASSWORD docker.pkg.github.com; } > /dev/null 2> /dev/null
fi

docker-compose up -d
docker logout
