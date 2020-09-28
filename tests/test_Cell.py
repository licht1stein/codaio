import pytest

from codaio import Cell
from tests.conftest import BASE_URL

BASE_TABLE_URL = BASE_URL + "/docs/doc_id/tables/table_id/"


class TestCell:
    @pytest.mark.parametrize("new_value", ["completely_new_value"])
    def test_set_value(self, mock_json_responses, main_table, new_value):

        responses = [
            ("rows?useColumnNames=False", "get_rows.json", {}),
            ("rows?useColumnNames=False", "get_updated_rows.json", {}),
            ("columns", "get_columns.json", {}),
            ("rows/index_id", "put_row.json", {"method": "PUT"}),
            ("rows/index_id", "get_updated_row.json", {}),
        ]
        mock_json_responses(responses, BASE_TABLE_URL)

        cell_a = main_table.rows()[0].cells()[0]
        assert isinstance(cell_a, Cell)
        cell_a.value = new_value
        assert cell_a.value == new_value
        fetched_again_cell = main_table.rows()[0].cells()[0]
        assert fetched_again_cell.value == new_value
