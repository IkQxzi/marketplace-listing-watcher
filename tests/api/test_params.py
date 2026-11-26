"""Tests only some params.
Larger tests may be split into their own modules, like test_payload.py"""

import pytest
import json

from marketplace_listing_watcher.api import IntRange


@pytest.mark.parametrize(
    "kwargs", [{"lower_bd": 1, "upper_bd": 5}, {"lower_bd": 1}, {"upper_bd": 1}]
)
def test_int_range_accepts_valid_bounds(kwargs):
    IntRange(**kwargs)


def test_int_range_rejects_lower_above_upper():
    with pytest.raises(ValueError):
        IntRange(lower_bd=5, upper_bd=1)


def test_int_range_serialisation():
    ir = IntRange(lower_bd=4, upper_bd=6)
    print(ir.model_dump(context="api"))
    print(json.dumps(ir.model_dump(), indent=2))
