import json
import types
from functools import partial
from unittest.mock import patch
from urllib.parse import urljoin

from django.test import override_settings

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


@pytest.fixture
def primary_validator_mock(outer_web_mock, blockchain_state_meta, pv_network_address):
    outer_web_mock.register_uri(
        outer_web_mock.POST,
        urljoin(pv_network_address, 'api/v1/signed-change-request/'),
        body=b'{}',
    )
    yield outer_web_mock


def raise_for_status(self):
    if self.status_code >= 400:
        raise HTTPError()


MOCKED_ADDRESSES = ('http://testserver/', 'http://preferred-node.non-existing-domain:8555/')


def client_method_wrapper(function, original_function, url, *args, **kwargs):
    # We need to convert requests to Django test client interface here
    for mocked_address in MOCKED_ADDRESSES:
        if url.startswith(mocked_address):
            break
    else:
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
    get_arguments = {
        'target': 'thenewboston_node.core.clients.node.requests_get',
        'new': partial(client_method_wrapper, api_client.get, requests_get),
    }
    post_arguments = {
        'target': 'thenewboston_node.core.clients.node.requests_post',
        'new': partial(client_method_wrapper, api_client.post, requests_post),
    }
    with patch(**get_arguments), patch(**post_arguments):
        yield


@pytest.fixture(scope='session', autouse=True)
def celery_configuration():
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        # For some reason we need to import the app to make the setting work
        from thenewboston_node.project.celery import app  # noqa: F401
        yield
