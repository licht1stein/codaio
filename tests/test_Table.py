import time

import pytest

from codaio import Column, Cell, Row, err
from tests.fixtures import coda, test_doc, main_table


@pytest.mark.usefixtures(coda.__name__, test_doc.__name__, main_table.__name__)
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
        cell_1 = Cell(columns[0], "unique_value_1")
        cell_2 = Cell(columns[1], "unique_value_2")
        result = main_table.upsert_row([cell_1, cell_2])
        assert result["status"] == 202
        rows = None
        count = 0
        while not rows:
            count += 1
            rows = main_table.find_row_by_column_id_and_value(
                cell_1.column.id, cell_1.value
            )
            if count > 20:
                pytest.fail("Row not added to table after 20 seconds")
            time.sleep(1)
        row = rows[0]
        assert isinstance(row, Row)
        assert row[cell_1.column.id].value == cell_1.value
        assert row[cell_2.column.id].value == cell_2.value

    def test_upsert_rows(self, main_table):
        columns = main_table.columns()

        rows = []
        for row in range(1, 11):
            rows.append(
                [Cell(column, f"value-{str(row)}-{column.name}") for column in columns]
            )

        result = main_table.upsert_rows(rows)

        assert result["status"] == 202

        key_column = columns[0]

        cell_to_update_1 = Cell(key_column, f"value-5-{columns[0].name}")
        cell_to_update_2 = Cell(columns[1], "updated_value")

        row_to_update = [cell_to_update_1, cell_to_update_2]

        result = main_table.upsert_rows([row_to_update], key_columns=[key_column])

        assert result["status"] == 202

        updated_rows = None
        while not updated_rows:
            updated_rows = main_table.find_row_by_column_id_and_value(
                cell_to_update_1.column.id, cell_to_update_1.value
            )
            time.sleep(1)

        assert len(updated_rows) == 1

        updated_row = updated_rows[0]
        assert (
            updated_row.get_cell_by_column_id(columns[1].id).value
            == cell_to_update_2.value
        )
