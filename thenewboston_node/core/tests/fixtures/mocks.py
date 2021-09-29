import json
import types
from functools import partial
from unittest.mock import patch
from urllib.parse import urljoin

import httpretty
import pytest
from requests.exceptions import HTTPError

from thenewboston_node.core.clients.node import requests_get, requests_post


@pytest.fixture(autouse=True)
def outer_web_mock():
    """
    This mock should prevent any accidental access to outer services during
    test runs
    """

    httpretty.enable(verbose=True, allow_net_connect=False)
    yield httpretty
    httpretty.disable()
    httpretty.reset()


@pytest.fixture
def node_mock(outer_web_mock, blockchain_state_meta, another_node_network_address):
    outer_web_mock.register_uri(
        outer_web_mock.GET,
        urljoin(another_node_network_address, 'api/v1/blockchain-states-meta/'),
        body=json.dumps({
            'count': 1,
            'results': [blockchain_state_meta],
        }),
    )
    yield outer_web_mock


def raise_for_status(self):
    if self.status_code >= 400:
        raise HTTPError()


def client_method_wrapper(function, original_function, url, *args, **kwargs):
    # We need to convert requests to Django test client interface here
    if not url.startswith('http://testserver/'):
        return original_function(url, *args, **kwargs)

    # Convert `json` to `data`
    json_ = kwargs.pop('json', None)
    if json_ is not None:
        kwargs['data'] = json_

    # Convert headers
    headers = kwargs.pop('headers', None)
    if headers:
        # TODO(dmu) LOW: Improve dealing with content type. Looks over engineered now
        content_type = headers.get('Content-Type')
        if content_type:
            kwargs['content_type'] = content_type
        kwargs.update(**headers)

    response = function(url, *args, **kwargs)
    response.raise_for_status = types.MethodType(raise_for_status, response)
    return response


@pytest.fixture
def node_mock_for_node_client(api_client):
    with patch(
        'thenewboston_node.core.clients.node.requests_get',
        new=partial(client_method_wrapper, api_client.get, requests_get)
    ):
        with patch(
            'thenewboston_node.core.clients.node.requests_post',
            new=partial(client_method_wrapper, api_client.post, requests_post)
        ):
            yield
