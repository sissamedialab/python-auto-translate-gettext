"""Tests related to the hide/unhide processing."""

import pytest

from po_translate import hide_variables


@pytest.mark.parametrize(
    ("text", "expected_result", "expected_placeholders"),
    [
        (
            "aaa {self.journal} bbb",
            "aaa 🤦 bbb",
            {"🤦": "{self.journal}"},
        ),
        (
            "Recipient user: {self.user if self.user else self.email} - journal: {self.journal}",
            "Recipient user: 🤦 - journal: 💆",
            {
                "🤦": "{self.user if self.user else self.email}",
                "💆": "{self.journal}",
            },
        ),
        (
            "release %(user)s and %(other)s",
            "release 🤦 and 💆",
            {
                "🤦": "%(user)s",
                "💆": "%(other)s",
            },
        ),
    ],
)
def test_hidevars(text: str, expected_result: str, expected_placeholders: dict) -> None:
    result, placeholders = hide_variables(text)
    assert result == expected_result
    assert placeholders == expected_placeholders
