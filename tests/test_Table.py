import time

import pytest

from codaio import Cell, Column, Row, err


@pytest.fixture
def mock_table_responses(mock_json_responses):
    base_table_url = "https://coda.io/apis/v1beta1/docs/doc_id/tables/table_id/"
    responses = [
        ("rows?useColumnNames=False", "get_rows.json", {}),
        ("columns", "get_columns.json", {}),
        ("column/column_id", "get_column.json", {}),
        ("rows/index_id", "get_row.json", {}),
        ("rows", "empty.json", {"method": "POST"}),
        ("rows?useColumnNames=False", "get_added_rows.json", {}),
        ("rows/index_id", "empty.json", {"method": "DELETE"}),
        (
            "rows?useColumnNames=False&query=column_id%3A%22value-Alpha%22",
            "get_row_by_query.json",
            {},
        ),
        (
            "rows?useColumnNames=False&query=column_id%3A%22value-5-Alpha%22",
            "get_updated_row_by_query.json",
            {},
        ),
        ("rows/no_such_id", "row_not_found.json", {"status": 404}),
    ]
    mock_json_responses(responses, base_url=base_table_url)


@pytest.mark.usefixtures("mock_table_responses")
class TestTable:
    def test_columns(self, main_table):
        assert main_table.columns()
        assert isinstance(main_table.columns()[0], Column)

    def test_get_column_by_id(self, main_table):
        columns = main_table.columns()
        for col in columns:
            assert main_table.get_column_by_id(col.id) == col
        with pytest.raises(err.CodaError):
            main_table.get_column_by_id("no_such_id")

    def test_get_row_by_id(self, main_table):
        rows = main_table.rows()
        for row in rows:
            fetched_row = main_table.get_row_by_id(row.id)
            assert fetched_row == row
        with pytest.raises(err.NotFound):
            main_table.get_row_by_id("no_such_id")

    def test_table_getitem(self, main_table):
        assert main_table[main_table.rows()[0].id] == main_table.rows()[0]
        assert main_table[main_table.rows()[0]] == main_table.rows()[0]

    def test_upsert_row(self, main_table):
        columns = main_table.columns()
        cell_1 = Cell(columns[0], f"value-{columns[0].name}")
        cell_2 = Cell(columns[1], f"value-{columns[1].name}")
        result = main_table.upsert_row([cell_1, cell_2])
        assert result["status"] == 202
        rows = main_table.find_row_by_column_id_and_value(
            cell_1.column.id, cell_1.value
        )
        row = rows[0]
        assert isinstance(row, Row)
        assert row[cell_1.column.id].value == cell_1.value
        assert row[cell_2.column.id].value == cell_2.value

    def test_upsert_rows_by_column_id(self, main_table):
        existing_rows = main_table.rows()

        for row in existing_rows:
            main_table.delete_row(row)

        result = main_table.upsert_rows(
            [
                [
                    Cell(column.id, f"value-{str(row)}-{column.name}")
                    for column in main_table.columns()
                ]
                for row in range(1, 6)
            ]
        )
        assert result["status"] == 202

        saved_rows = main_table.rows()
        assert len(saved_rows) == 5
        assert all([isinstance(row, Row) for row in saved_rows])

    def test_upsert_existing_rows(self, main_table):
        columns = main_table.columns()
        key_column = columns[0]

        result = main_table.upsert_rows(
            [
                [Cell(column, f"value-{str(row)}-{column.name}") for column in columns]
                for row in range(1, 11)
            ]
        )

        assert result["status"] == 202

        cell_to_update_1 = Cell(key_column, f"value-5-{columns[0].name}")
        cell_to_update_2 = Cell(columns[1], "updated_value")

        row_to_update = [cell_to_update_1, cell_to_update_2]

        result = main_table.upsert_rows([row_to_update], key_columns=[key_column])

        assert result["status"] == 202
        updated_rows = main_table.find_row_by_column_id_and_value(
            cell_to_update_1.column.id, cell_to_update_1.value
        )
        assert len(updated_rows) == 1

        updated_row = updated_rows[0]
        assert (
            updated_row.get_cell_by_column_id(columns[1].id).value
            == cell_to_update_2.value
        )
