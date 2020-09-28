import pytest
from pathlib import Path
import responses
import json
from codaio import Coda, Document


@pytest.fixture(scope="session")
def coda():
    API_KEY = "ANY_KEY"
    return Coda(API_KEY)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def mock_unauthorized_response(mock_json_response):
    def _mock_unauthorized_response(method):
        url = "https://coda.io/apis/v1beta1/"
        json_file = "unauthorized.json"
        mock_json_response(url, json_file, status=401, method=method)

    return _mock_unauthorized_response


@pytest.fixture
def mock_json_response(mocked_responses):
    """
    register mocked json responses.

    For a url, return the content of a json file in the /test/data/ folder.
    """

    def _mock_json_response_from_file(
        url, filename, method="GET", status=202, **kwargs
    ):
        test_directory = Path(__file__).parent
        relative_data_directory = "data/"
        json_path = Path(test_directory / relative_data_directory / filename).resolve()
        with open(json_path) as json_file:
            json_content = json.load(json_file)

        method_map = {
            "ANY": responses.UNSET,
            "GET": responses.GET,
            "POST": responses.POST,
            "PUT": responses.PUT,
            "DELETE": responses.DELETE,
            "PATCH": responses.PATCH,
            "HEAD": responses.HEAD,
        }

        mocked_responses.add(
            method_map.get(method), url, json=json_content, status=status, **kwargs
        )

    return _mock_json_response_from_file


@pytest.fixture
def mock_json_responses(mock_json_response):
    """
    register multiple json repsonses.

    Responses should be passed as a list of (url, filename, kwargs) tupples.
    """

    def _mock_json_responses(responses, base_url=None):
        for url, filename, kwargs in responses:
            mock_json_response(base_url + url, filename, **kwargs)

    return _mock_json_responses


@pytest.fixture
def main_document(coda, mock_json_response):
    mock_json_response("https://coda.io/apis/v1beta1/docs/doc_id/", "get_doc.json")
    return Document("doc_id", coda=coda)


@pytest.fixture
def main_table(main_document, mock_json_response):
    mock_json_response(
        "https://coda.io/apis/v1beta1/docs/doc_id/tables/table_id", "get_table.json"
    )
    return main_document.get_table("table_id")
