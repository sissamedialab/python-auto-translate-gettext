"""Tests related to the hide/unhide processing."""

from po_translate import hide_variables


def test_hidevars() -> None:
    x = "aaa {self.journal} bbb"
    y, d = hide_variables(x)
    assert y == "aaa __PLACEHOLDER_0__ bbb"
