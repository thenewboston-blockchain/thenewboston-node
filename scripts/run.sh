#!/usr/bin/env bash

set -e
poetry run python -m thenewboston_node.manage migrate

# TODO(dmu) MEDIUM: We do not really need to collect static, since we are using Whitenoise
poetry run python -m thenewboston_node.manage collectstatic

# TODO(dmu) MEDIUM: Unhardcode /var/lib/blockchain
export BLOCKCHAIN_PATH=/var/lib/blockchain
if [ ! "$(ls -A $BLOCKCHAIN_PATH)" ]; then
  poetry run python -m thenewboston_node.manage convert_account_root_file $ARF_URL
  if [ $? -ne 0 ]; then
    cp -R /opt/project/blockchain/* $BLOCKCHAIN_PATH
  fi
fi

poetry run daphne -b 0.0.0.0 thenewboston_node.project.asgi:application
