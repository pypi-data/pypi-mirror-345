#!/usr/bin/env -S pytest -vvv

"""
Unit tests for indexing operations
"""

import numpy as np

from oxvox.indexing import indices_by_field
from oxvox.util import _default_dtype


PLATFORM_DTYPE = _default_dtype()


TEST_ARRAY = np.array(
    [
        ("foo", 2, 0.5, 15),
        ("bar", 3, 1.5, 15),
        ("baz", 2, 2.5, 30),
        ("bat", 3, 3.5, 30),
        ("bet", 4, 4.5, 15),
        ("bot", 4, 5.5, 30),
    ],
    dtype=[
        ("field", "|O"),
        ("a", np.int32),
        ("b", np.float32),
        ("c", np.int32),
    ],
)


def test_indices_by_field() -> None:
    """
    Test that indices_by_field returns the correct row indices for each value in a given field
    """

    # Test a single field
    for computed, expected in zip(
        sorted(list(indices_by_field(arr=TEST_ARRAY, fields="a"))),
        [
            (2, [0, 2]),
            (3, [1, 3]),
            (4, [4, 5]),
        ],
    ):
        assert computed[0].tolist() == expected[0]
        assert computed[1].tolist() == expected[1]

    # Test multiple fields
    for computed, expected in zip(
        sorted(
            list(indices_by_field(arr=TEST_ARRAY, fields=["a", "c"])),
            key=lambda x: tuple(x[0]),
        ),
        [
            ((2, 15), [0]),
            ((2, 30), [2]),
            ((3, 15), [1]),
            ((3, 30), [3]),
            ((4, 15), [4]),
            ((4, 30), [5]),
        ],
    ):
        assert computed[0].tolist() == expected[0]
        assert computed[1].tolist() == expected[1]
