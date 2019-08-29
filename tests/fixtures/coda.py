import datetime as dt

import pytest
from envparse import env

from codaio import Coda, Document


@pytest.fixture(scope="session")
def coda():
    API_KEY = env("CODA_API_KEY", cast=str)
    return Coda(API_KEY)


@pytest.fixture
def doc_id(coda):
    data = coda.create_doc("Test_Doc")
    doc_id = data["id"]
    yield doc_id
    coda.delete_doc(doc_id)


@pytest.fixture
def test_doc(coda):
    test_doc_id = env("TEST_DOC_ID")
    copy_id = coda.create_doc(
        f"Test_Dod_{dt.datetime.utcnow().timestamp()}", source_doc=test_doc_id
    )["id"]
    yield Document(copy_id, coda=coda)
    coda.delete_doc(copy_id)
