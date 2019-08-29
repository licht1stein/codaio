import datetime as dt

import pytest

from codaio import Coda
from codaio import err

from tests.fixtures import coda


@pytest.mark.usefixtures(coda.__name__)
class TestCoda:
    def test_init(self):
        coda = Coda("FAKE_API_KEY")
        assert isinstance(coda, Coda)

    def test_init_fail_connect(self):
        coda = Coda("FAKE_API_KEY")
        with pytest.raises(err.CodaError):
            coda.account()

    def test_list_documents(self, coda):
        docs = coda.list_docs()
        assert docs

    def test_create_doc__delete_doc(self, coda):
        response = coda.create_doc(f"Test_Document_{dt.datetime.utcnow().timestamp()}")
        assert response.status_code == 201
        doc_id = response.json()["id"]
        assert doc_id
        coda.delete_doc(doc_id)
        with pytest.raises(err.CodaError):
            coda.get_doc(doc_id)
