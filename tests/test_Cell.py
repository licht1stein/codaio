import pytest
from tests.fixtures import coda, main_table, test_doc

from codaio import Cell


@pytest.mark.usefixtures(coda.__name__, test_doc.__name__, main_table.__name__)
class TestCell:
    @pytest.mark.parametrize("new_value", ["completely_new_value"])
    def test_set_value(self, main_table, new_value):
        cell_a = main_table.rows()[0].cells()[0]
        assert isinstance(cell_a, Cell)
        cell_a.value = new_value
        assert cell_a.value == new_value
        fetched_again_cell = main_table.rows()[0].cells()[0]
        assert fetched_again_cell.value == new_value
