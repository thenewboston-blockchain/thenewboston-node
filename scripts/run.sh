#!/usr/bin/env bash

set -e
python -m thenewboston_node.manage migrate
python -m thenewboston_node.manage collectstatic
# TODO(dmu) HIGH: Migrate to a production grade server instead of Django built-in server
python -m thenewboston_node.manage runserver 0.0.0.0:8000
