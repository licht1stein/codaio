import pytest

from codaio import Document, err


class TestDocument:
    def test_raise_no_api_key(self):
        with pytest.raises(err.NoApiKey):
            Document.from_environment("doc_id")

    @pytest.mark.parametrize(
        "filt, output",
        [
            ({"column_name": "foo", "value": "bar"}, {"query": '"foo":"bar"'}),
            ({"column_id": "foo", "value": "bar"}, {"query": 'foo:"bar"'}),
        ],
    )
    def test_parse_filter(self, filt, output):
        assert Document._parse_filter(filt) == output

    @pytest.mark.parametrize(
        "filt",
        [
            {"column_id": "foo"},
            {"column_name": "foo"},
            {"value": "bar"},
            {},
            {"foo": "bar"},
        ],
    )
    def test_parse_filter_raise(self, filt):
        with pytest.raises(err.InvalidFilter):
            Document._parse_filter(filt)
