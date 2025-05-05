# ruff: noqa: D100, D102, D103, S101, S106
"""Unit tests for do_check method in ItemsFilter class."""

import pytest

from feed2fedi.control import Checks
from feed2fedi.control import ItemsFilter


def test_items_filter_check() -> None:
    """Test do_check method in ItemsFilter."""
    item = ItemsFilter(check=Checks.NONE, check_params="")
    assert not item.do_check(item="test item")

    item.check = Checks.ANY
    assert item.do_check(item="test_item")

    item.check = Checks.REGEX
    item.check_params = r"\d+"
    assert item.do_check(item={"summary": "1st summary"})
    assert not item.do_check(item={"summary": "a summary paragraph"})

    item.check_params = 0.0
    with pytest.raises(Exception):  # noqa B017
        item.do_check(item="blah blah")

    item.check_params = r"\d+"
    item.check = "blah"
    with pytest.raises(Exception):  # noqa B017
        item.do_check(item="blah blah")
