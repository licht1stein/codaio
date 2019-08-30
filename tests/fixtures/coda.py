import datetime as dt
import re
import time

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


@pytest.fixture(scope="function")
def test_doc(coda):
    test_doc_id = env("TEST_DOC_ID")
    existing_docs = coda.list_docs()
    for doc in existing_docs["items"]:
        if re.match(r"Test_Do\S+_\d+", doc["name"]):
            coda.delete_doc(doc["id"])

    copy_id = coda.create_doc(
        f"Test_Doc_{dt.datetime.utcnow().timestamp()}", source_doc=test_doc_id
    )["id"]
    time.sleep(2)
    yield Document(copy_id, coda=coda)
    coda.delete_doc(copy_id)


@pytest.fixture(scope="function")
def main_table(test_doc):
    tables = test_doc.list_tables()
    assert tables
    return [t for t in tables if t.name == "Main"][0]
