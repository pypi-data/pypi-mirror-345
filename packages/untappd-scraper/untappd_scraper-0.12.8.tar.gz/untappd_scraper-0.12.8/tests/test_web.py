"""Test web utils."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    "user_id, venue_id, brewery_id, beer_id, search, page, query, expected",
    [
        ("", "", "", "", False, "", None, "https://untappd.com"),
        ("123", "", "", "", False, "", None, "https://untappd.com/user/123"),
        ("", "456", "", "", False, "", None, "https://untappd.com/venue/456"),
        ("", "", "789", "", False, "", None, "https://untappd.com/brewery/789"),
        ("", "", "", "101112", False, "", None, "https://untappd.com/beer/101112"),
        ("", "", "", "", True, "", None, "https://untappd.com/search"),
        ("", "", "", "", False, "page1", None, "https://untappd.com/page1"),
        ("", "", "", "", False, "/v/page1", None, "https://untappd.com/v/page1"),
        ("", "", "", "", False, "", {"key": "value"}, "https://untappd.com?key=value"),
    ],
)
def test_url_of(
    user_id: str,
    venue_id: str,
    brewery_id: str,
    beer_id: str,
    search: bool,
    page: str,
    query: dict[str, str | int] | None,
    expected: str,
) -> None:
    """Test URL generation."""
    from untappd_scraper.web import url_of

    result = url_of(
        user_id=user_id,
        venue_id=venue_id,
        brewery_id=brewery_id,
        beer_id=beer_id,
        search=search,
        page=page,
        query=query,
    )

    assert result == expected
    assert result.startswith("https://untappd.com")
