import pytest

from src.iterable_tompy import first
from src.iterable_tompy.exceptions import InputNotIterableError, EmptyIterableError


def test_first_non_iterator_failure():
    # Setup
    float0: float = 0.25

    # Validation
    with pytest.raises(InputNotIterableError):
        # noinspection PyTypeChecker
        first(float0)


def test_first_empty_failure():
    # Setup
    list0: list = []

    # Validation
    with pytest.raises(EmptyIterableError):
        first(list0)


def test_first_single_item_success():
    # Setup
    integer0: int = 0
    integer1: int = 0
    list0: list = [integer1]

    # Execution
    integer2: int = first(list0)

    # Validation
    assert integer0 == integer2


def test_first_multiple_items_success():
    # Setup
    integer0: int = 0
    integer1: int = 0
    integer2: int = 1
    integer3: int = 2
    list0: list = [integer1, integer2, integer3]

    # Execution
    integer4: int = first(list0)

    # Validation
    assert integer0 == integer4
