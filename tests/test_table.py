import pytest

from codaio import Column
from tests.fixtures import coda, test_doc


@pytest.mark.usefixtures(coda.__name__, test_doc.__name__)
class TestTable:
    @pytest.fixture
    def main_table(self, test_doc):
        tables = test_doc.list_tables()
        assert tables
        return [t for t in tables if t.name == "Main"][0]

    def test_columns(self, main_table):
        assert main_table.columns()
        assert isinstance(main_table.columns()[0], Column)
