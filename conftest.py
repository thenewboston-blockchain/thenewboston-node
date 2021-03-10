import os

# TODO(dmu) LOW: For some reason pytest does not recognize conftest.py if being placed into `thenewboston_node`
#                package. Fix it.

# Set on the earliest possible moment
os.environ['PYTEST_RUNNING'] = 'true'

from thenewboston_node.business_logic.tests.fixtures import *  # noqa: F401, F403, E402
