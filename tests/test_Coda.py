import pytest

from codaio import Coda, err
from tests.conftest import BASE_URL

BASE_DOC_URL = BASE_URL + "/docs"


class TestCoda:
    def test_init(self, coda):
        assert isinstance(coda, Coda)

    def test_raise_GET(self, coda, mock_unauthorized_response):
        mock_unauthorized_response("GET")
        with pytest.raises(err.CodaError):
            coda.get("/")

    def test_raise_POST(self, coda, mock_unauthorized_response):
        mock_unauthorized_response("POST")
        with pytest.raises(err.CodaError):
            coda.post("/", {})

    def test_raise_PUT(self, coda, mock_unauthorized_response):
        mock_unauthorized_response("PUT")
        with pytest.raises(err.CodaError):
            coda.put("/", {})

    def test_raise_DELETE(self, coda, mock_unauthorized_response):
        mock_unauthorized_response("DELETE")
        with pytest.raises(err.CodaError):
            coda.delete("/")

    def test_list_documents(self, coda, mock_json_response):
        url = BASE_DOC_URL
        json_file = "get_docs.json"

        mock_json_response(url, json_file)

        docs = coda.list_docs()
        assert docs

    def test_create_doc(self, coda, mock_json_response):
        url = BASE_DOC_URL
        json_file = "get_doc.json"
        mock_json_response(url, json_file, method="POST")

        response = coda.create_doc("Test_Document")
        doc_id = response["id"]
        assert doc_id

    def test_get_doc(self, coda, mock_json_response):
        doc_id = "doc_id"
        url = BASE_DOC_URL + "/doc_id"
        json_file = "get_doc.json"
        mock_json_response(url, json_file)

        data = coda.get_doc(doc_id)
        assert data["id"] == doc_id

    def test_delete_doc(self, coda, mock_json_response):
        doc_id = "doc_id"
        delete_url = BASE_DOC_URL + "/doc_id"
        json_file = "empty.json"
        mock_json_response(delete_url, json_file, method="DELETE", status=202)

        coda.delete_doc(doc_id)

        get_url = BASE_DOC_URL + "/doc_id"
        file_not_found_json = "doc_deleted.json"
        mock_json_response(get_url, file_not_found_json, status=404)

        with pytest.raises(err.CodaError):
            coda.get_doc(doc_id)
