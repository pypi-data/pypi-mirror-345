from typing import Iterable

import pytest

from src.iterable_tompy.exceptions import IndexOutOfBoundsError
from src.iterable_tompy.indices import indices_between_indices


def test_indices_between_indices_single_value_empty_output_success():
    # Setup
    start_index0: int = 0
    end_index0: int = 0
    length0: int = 1
    indices0: list[int] = []

    # Execution
    indices1: Iterable[int] = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)

    # Validation
    assert indices0 == list(indices1)


def test_indices_between_indices_multiple_values_not_wrapping_success():
    # Setup
    start_index0: int = 2
    end_index0: int = 5
    length0: int = 8
    indices0: list[int] = [2, 3, 4]

    # Execution
    indices1: Iterable[int] = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)

    # Validation
    assert indices0 == list(indices1)


def test_indices_between_indices_multiple_values_wrapping_success():
    # Setup
    start_index0: int = 4
    end_index0: int = 2
    length0: int = 6
    indices0: list[int] = [4, 5, 0, 1]

    # Execution
    indices1: Iterable[int] = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)

    # Validation
    assert indices0 == list(indices1)


def test_indices_between_indices_start_before_range_failure():
    # Setup
    start_index0: int = -1
    end_index0: int = 2
    length0: int = 5

    # Validation
    with pytest.raises(IndexOutOfBoundsError):
        _ = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)


def test_indices_between_indices_end_before_range_failure():
    # Setup
    start_index0: int = 1
    end_index0: int = -2
    length0: int = 5

    # Validation
    with pytest.raises(IndexOutOfBoundsError):
        _ = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)


def test_indices_between_indices_start_after_range_failure():
    # Setup
    start_index0: int = 2
    end_index0: int = 9
    length0: int = 6

    # Validation
    with pytest.raises(IndexOutOfBoundsError):
        _ = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)


def test_indices_between_indices_end_after_range_failure():
    # Setup
    start_index0: int = 8
    end_index0: int = 3
    length0: int = 7

    # Validation
    with pytest.raises(IndexOutOfBoundsError):
        _ = indices_between_indices(start_index=start_index0, end_index=end_index0, length=length0)
