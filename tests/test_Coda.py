import datetime as dt

import pytest

from codaio import Coda
from codaio import err

from tests.fixtures import coda, doc_id


@pytest.mark.usefixtures(coda.__name__, doc_id.__name__)
class TestCoda:
    @pytest.fixture()
    def fake_coda(self):
        return Coda("foo")

    def test_init(self, fake_coda):
        assert isinstance(fake_coda, Coda)

    def test_raise_GET(self, fake_coda):
        with pytest.raises(err.CodaError):
            fake_coda.get("/")

    def test_raise_POST(self, fake_coda):
        with pytest.raises(err.CodaError):
            fake_coda.post("/", {})

    def test_raise_PUT(self, fake_coda):
        with pytest.raises(err.CodaError):
            fake_coda.put("/", {})

    def test_raise_DELETE(self, fake_coda):
        with pytest.raises(err.CodaError):
            fake_coda.delete("/")

    def test_list_documents(self, coda):
        docs = coda.list_docs()
        assert docs

    def test_create_doc__delete_doc(self, coda):
        response = coda.create_doc(f"Test_Document_{dt.datetime.utcnow().timestamp()}")
        doc_id = response["id"]
        assert doc_id
        coda.delete_doc(doc_id)
        with pytest.raises(err.CodaError):
            coda.get_doc(doc_id)

    def test_get_doc(self, coda, doc_id):
        data = coda.get_doc(doc_id)
        assert data["id"] == doc_id
