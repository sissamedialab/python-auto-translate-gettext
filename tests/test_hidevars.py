"""Tests related to the hide/unhide processing."""

import pytest

from po_translate import hide_variables


@pytest.mark.parametrize(
    ("text", "expected_result", "expected_placeholders"),
    [
        (
            "aaa {self.journal} bbb",
            "aaa __PLACEHOLDER_0__ bbb",
            {"__PLACEHOLDER_0__": "{self.journal}"},
        ),
        (
            "Recipient user: {self.user if self.user else self.email} - journal: {self.journal}",
            "Recipient user: __PLACEHOLDER_0__ - journal: __PLACEHOLDER_1__",
            {
                "__PLACEHOLDER_0__": "{self.user if self.user else self.email}",
                "__PLACEHOLDER_1__": "{self.journal}",
            },
        ),
        (
            "release %(user)s and %(other)s",
            "release __PLACEHOLDER_0__ and __PLACEHOLDER_1__",
            {
                "__PLACEHOLDER_0__": "%(user)s",
                "__PLACEHOLDER_1__": "%(other)s",
            },
        ),
    ],
)
def test_hidevars(text: str, expected_result: str, expected_placeholders: dict) -> None:
    result, placeholders = hide_variables(text)
    assert result == expected_result
    assert placeholders == expected_placeholders
