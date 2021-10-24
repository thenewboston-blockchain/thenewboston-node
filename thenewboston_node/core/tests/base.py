from contextlib import contextmanager

from thenewboston_node.core.clients.node import NodeClient


@contextmanager
def force_node_client(node_client: NodeClient):
    try:
        NodeClient.set_instance_cache(node_client)
        yield
    finally:
        NodeClient.clear_instance_cache()
