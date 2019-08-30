import time

import pytest

from codaio import Column, Cell, Row, err
from tests.fixtures import coda, test_doc, main_table


@pytest.mark.usefixtures(coda.__name__, test_doc.__name__, main_table.__name__)
class TestRow:
    def test_get_cell_by_column_id(self, main_table):
        row_a: Row = main_table.rows()[0]
        cell_a: Cell = row_a.cells()[0]
        assert isinstance(cell_a, Cell)
        fetched_cell = row_a.get_cell_by_column_id(cell_a.column.id)
        assert isinstance(fetched_cell, Cell)

    def test_row_getitem(self, main_table):
        row_a: Row = main_table.rows()[0]
        column_a: Column = main_table.columns()[0]
        assert isinstance(row_a, Row)
        assert isinstance(column_a, Column)

        res_cell = row_a[column_a]
        assert isinstance(res_cell, Cell)
        assert res_cell.column == column_a
        assert res_cell.row == row_a

    def test_refresh(self, main_table):
        row_a: Row = main_table.rows()[0]
        assert row_a.refresh()
