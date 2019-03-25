
import json
import os
import pytest
import requests_mock

from app import create_app
from tests.testing_config import TEST_CONFIG


with open(os.path.join(
              os.path.dirname(__file__),
              'test_data/test_github_search_api_first_page_response.json'), 'rb') as f:
    test_github_search_api_first_page_response = json.loads(f.read().decode('utf8').rstrip())


with open(os.path.join(
              os.path.dirname(__file__),
              'test_data/test_github_search_api_last_page_response.json'), 'rb') as f:
    test_github_search_api_last_page_response = json.loads(f.read().decode('utf8').rstrip())


github_url = TEST_CONFIG['GITHUB_BASE_QUERY']


@pytest.fixture
def app():
    with requests_mock.Mocker() as mock_request:
        mock_request.get(github_url + str(1), json=test_github_search_api_first_page_response)
        mock_request.get(github_url + str(10), json=test_github_search_api_last_page_response)

        app = create_app(TEST_CONFIG)

        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


