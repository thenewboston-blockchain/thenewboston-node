from urllib.parse import urljoin


def test_get_latest_blockchain_state_meta_by_network_address(
    node_client, node_mock, blockchain_state_meta, another_node_network_address
):
    result = node_client.get_latest_blockchain_state_meta_by_network_address(another_node_network_address)
    assert result == blockchain_state_meta
    assert node_mock.latest_requests()[-1].url.startswith(
        urljoin(another_node_network_address, 'api/v1/blockchain-states-meta/')
    )
