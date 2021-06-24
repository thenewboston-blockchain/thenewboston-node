#!/usr/bin/env bash

set -e
poetry run python -m thenewboston_node.manage migrate

# TODO(dmu) MEDIUM: We do not really need to collect static, since we are using Whitenoise
poetry run python -m thenewboston_node.manage collectstatic

# TODO(dmu) MEDIUM: Unhardcode /var/lib/blockchain
export BLOCKCHAIN_PATH=/var/lib/blockchain
if [ ! "$(ls -A $BLOCKCHAIN_PATH)" ]; then
  echo 'Downloading the latest alpha account root file...'
  poetry run python -m thenewboston_node.manage convert_account_root_file ${ARF_URL} || true
  if [ ! "$(ls -A $BLOCKCHAIN_PATH)" ]; then
    echo 'Could not download the latest alpha account root file, using build time copy as failover'
    cp -R /opt/project/blockchain/* $BLOCKCHAIN_PATH
  else
    echo 'Downloaded the latest alpha account root file'
  fi
fi

poetry run daphne -b 0.0.0.0 thenewboston_node.project.asgi:application
