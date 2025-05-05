from itertools import chain
from typing import Collection, Iterable

from .exceptions import IndexOutOfBoundsError


def indices_around_index(index: int, collection: Collection) -> list[int]:
    """Indices from first after index to last of collection, and from head of collection to last before index."""
    range_from_after_index_to_last: range = range(index + 1, len(collection))
    range_from_head_to_before_index: range = range(0, index)
    indices: list[int] = list(range_from_after_index_to_last) + list(range_from_head_to_before_index)
    return indices


def indices_between_indices(start_index: int, end_index: int, length: int) -> Iterable[int]:
    """Sequence of indices, wrapping around the end of a sequence of values,
        starting from and including start index, until and excluding end index."""
    if start_index < 0 or end_index < 0 or start_index >= length or end_index >= length:
        raise IndexOutOfBoundsError(f"Start '{start_index}' or end '{end_index}' index "
                                    f"is not within the bounds of the length value '{length}'.")

    indices: Iterable[int] | None = None

    if start_index <= end_index:
        indices = range(start_index, end_index)
    elif start_index > end_index:
        indices = chain(range(start_index, length), range(0, end_index))

    return indices
