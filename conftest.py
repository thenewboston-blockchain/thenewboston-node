import os

# TODO(dmu) LOW: For some reason pytest does not recognize conftest.py if being placed into `thenewboston_node`
#                package. Fix it.

# Set on the earliest possible moment
os.environ['PYTEST_RUNNING'] = 'true'
