import pytest
from envparse import env

from codaio import Coda


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
