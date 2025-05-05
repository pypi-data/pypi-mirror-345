import math
import itertools
import os
import sys
import re
from pathlib import Path

if __name__ == "__main__":  # to make the tests run without the pytest cli
    file_folder = os.path.dirname(__file__)
    os.chdir(file_folder)
    sys.path.insert(0, file_folder + "/../xlwings_utils")

import pytest

import xlwings_utils as xwu


def test_block():
    this_block = xwu.block(number_of_rows=4, number_of_columns=6)
    this_block[1, 2] = 2
    this_block[2, 5] = 25
    assert this_block.dict == {(1, 2): 2, (2, 5): 25}
    assert this_block.as_list_of_lists == [
        [None, 2, None, None, None, None],
        [None, None, None, None, 25, None],
        [None, None, None, None, None, None],
        [None, None, None, None, None, None],
    ]
    assert this_block.as_minimal_list_of_lists == [[None, 2, None, None, None], [None, None, None, None, 25]]
    assert this_block.number_of_rows == 4
    assert this_block.number_of_columns == 6
    assert this_block.maximum_row == 2
    assert this_block.maximum_column == 5

    this_block.number_of_rows = 99
    this_block.number_of_columns = 99
    assert this_block.maximum_row == 2
    assert this_block.maximum_column == 5

    this_block.number_of_rows = 1
    this_block.number_of_columns = 3
    assert this_block.as_list_of_lists == [[None, 2, None]]
    assert this_block.as_minimal_list_of_lists == [[None, 2]]


def test_block_from_list_of_lists():
    this_block = xwu.block.from_list_of_lists([[1, 2, 3], [4, 5, 6]])
    assert this_block.dict == {(1, 1): 1, (1, 2): 2, (1, 3): 3, (2, 1): 4, (2, 2): 5, (2, 3): 6}
    assert this_block.as_list_of_lists == [[1, 2, 3], [4, 5, 6]]
    assert this_block.as_minimal_list_of_lists == [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        this_block.number_of_rows = 0
    with pytest.raises(ValueError):
        this_block.number_of_columns = 0
    with pytest.raises(ValueError):
        this_block = xwu.block(0, 1)
    with pytest.raises(ValueError):
        this_block = xwu.block(1, 0)


def test_block_one_dimension():
    this_block = xwu.block.from_list_of_lists([1, 2, 3])
    assert this_block.as_list_of_lists == [[1, 2, 3]]

    this_block = xwu.block.from_list_of_lists([1, 2, 3], column_like=True)
    assert this_block.as_list_of_lists == [[1], [2], [3]]


def test_block_scalar():
    this_block = xwu.block.from_list_of_lists(1, column_like=True)
    assert this_block.as_list_of_lists == [[1]]


if __name__ == "__main__":
    pytest.main(["-vv", "-s", "-x", __file__])
