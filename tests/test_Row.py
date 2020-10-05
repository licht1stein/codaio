import pytest

from codaio import Cell, Column, Row
from tests.conftest import BASE_URL


@pytest.fixture
def mock_row_responses(mock_json_responses):
    base_table_url = BASE_URL + "/docs/doc_id/tables/table_id/"
    responses = [
        ("rows?useColumnNames=False", "get_rows.json", {}),
        ("columns", "get_columns.json", {}),
        ("rows/index_id", "get_row.json", {}),
    ]
    mock_json_responses(responses, base_url=base_table_url)


@pytest.mark.usefixtures("mock_row_responses")
class TestRow:
    def test_get_cell_by_column_id(self, main_table, mock_json_responses):
        row_a: Row = main_table.rows()[0]
        cell_a: Cell = row_a.cells()[0]
        assert isinstance(cell_a, Cell)

        fetched_cell = row_a.get_cell_by_column_id(cell_a.column.id)
        assert isinstance(fetched_cell, Cell)

    def test_row_getitem(self, main_table, mock_json_responses):

        row_a: Row = main_table.rows()[0]
        column_a: Column = main_table.columns()[0]
        assert isinstance(row_a, Row)
        assert isinstance(column_a, Column)

        res_cell = row_a[column_a]
        assert isinstance(res_cell, Cell)
        assert res_cell.column == column_a
        assert res_cell.row == row_a

    def test_refresh(self, main_table, mock_json_responses):
        row_a: Row = main_table.rows()[0]
        assert row_a.refresh()
