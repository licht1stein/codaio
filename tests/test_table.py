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
        with pytest.raises(err.ColumnNotFound):
            main_table.get_column_by_id("no_such_id")

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
                pytest.fail("Row not added to table after 15 seconds")
            time.sleep(1)
        row = rows[0]
        assert isinstance(row, Row)
        assert row[cell_1.column.name].value == cell_1.value
        assert row[cell_2.column.name].value == cell_2.value
