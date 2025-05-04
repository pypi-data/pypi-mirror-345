import pytest
from chercher_plugin_rss import is_valid_url


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://example.com", True),
        ("ftp://example.com", False),
        ("http://example.com", True),
        ("example.com", False),
        ("https://", False),
        ("http://", False),
        ("http://localhost", True),
        ("example", False),
        ("", False),
    ],
)
def test_is_valid_url(url, expected):
    assert is_valid_url(url) == expected
