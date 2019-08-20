import pytest

from codaio import Document, err


class TestDocument:
    def test_raise_no_api_key(self):
        with pytest.raises(err.NoApiKey):
            Document.from_environment("doc_id")
