#!/usr/bin/env bash

set -e
wget https://raw.githubusercontent.com/thenewboston-developers/thenewboston-node/master/docker-compose.yml -O docker-compose.yml

if [ ! -f .env ]; then
cat <<EOF > .env
THENEWBOSTON_NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)
EOF
fi
