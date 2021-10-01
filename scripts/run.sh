#!/usr/bin/env bash

set -e

# We need to collect static files to make WhiteNoise work (and we need to do it here)
# TODO(dmu) LOW: Collect static once, not on every run (we need to have named volume for it)
poetry run python -m thenewboston_node.manage collectstatic

# TODO(dmu) LOW: Consider implementation of run-time node declaration watch dog
poetry run python -m thenewboston_node.manage ensure_node_declared

# TODO(dmu) CRITICAL: Remove second sync once normal new block notification mechanism is implemented
poetry run python -m thenewboston_node.manage sync_blockchain

# TODO(dmu) MEDIUM: We might reconsider using `daphne` after figuring out if we have IO-bound or
#                   CPU-bound application
poetry run daphne -b 0.0.0.0 -p 8555 thenewboston_node.project.asgi:application
