"""Test user scraping."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from untappd_scraper.user import User
from untappd_scraper.user_lists import WebUserList
from utpd_models_web.constants import UNTAPPD_BEER_HISTORY_SIZE

# sourcery skip: dont-import-test-modules
if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import MockResponse


@pytest.fixture
def user(
    _mock_user_get: None,
    # _mock_user_beer_history_get: None,
    _mock_user_venue_history_get: None,
    _mock_user_lists_get: None,
) -> User:
    return User("test")


# ----- Tests -----


def test_user(user: User) -> None:
    result = user

    assert result
    assert result.name
    assert result.user_id
    assert result.user_name


@pytest.mark.httpbin
@pytest.mark.usefixtures("_mock_user_404")
def test_user_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid"):
        User("123")  # ignored


def test_activity(user: User) -> None:
    result = user.activity()

    assert result
    assert result[0].checkin_id
    assert result[0].beer_id
    assert all("jpeg" in r.beer_label_url for r in result)
    assert all(r.brewery_url and "tba" not in r.brewery_url.casefold() for r in result)


@pytest.mark.webtest
def test_activity_mw1414() -> None:
    result = User("mw1414").activity()

    assert result


@pytest.fixture(scope="module")
def wardy_user() -> User:
    """Create a real, web-scraped user."""
    return User("mw1414")


@pytest.mark.webtest
def test_beer_history(wardy_user: User) -> None:
    result = wardy_user.beer_history()

    assert result
    assert len(result.results) == UNTAPPD_BEER_HISTORY_SIZE
    assert len({b.beer_id for b in result.results}) == UNTAPPD_BEER_HISTORY_SIZE
    assert result.results[0].beer_name
    assert result.results[0].brewery_name
    assert result.results[0].recent_checkin_id
    assert not result.found_all  # way more than one page of uniques
    assert "total_found=25," in repr(result)
    assert all("assets" in r.beer_label_url for r in result.results)
    assert all(r.brewery_url and r.brewery_url != "TBA" for r in result.results)
    assert all(r.beer_label_url for r in result.results)


@pytest.mark.webtest
def test_beer_brewery_history_alesmith(wardy_user: User) -> None:
    # As of Apr 2025, Wardy had 31 Alesmith beers
    result = wardy_user.brewery_history(brewery_id=2471, max_resorts=1)

    assert result
    assert result.total_found
    assert result.found_all
    assert all(r.beer_label_url for r in result.results)


@pytest.mark.webtest
def test_beer_brewery_history_buckettys(wardy_user: User) -> None:
    # As of Apr 2025, Wardy had 84 bucketty's beers
    # and an English IPA was elusive in re-sorts
    result = wardy_user.brewery_history(brewery_id=484738, max_resorts=99)

    assert result
    assert len(result.results) > UNTAPPD_BEER_HISTORY_SIZE
    assert len(result.results) == 84  # NOTE fragile!
    assert result.found_all
    assert all(r.beer_label_url for r in result.results)


# NOTE this is huge. Probably should skip of limit resorts
@pytest.mark.webtest
def test_beer_brewery_history_4pines(wardy_user: User) -> None:
    max_resorts = 3
    # As of Apr 2025, Wardy had 569 4 Pines beers!!
    result = wardy_user.brewery_history(brewery_id=4254, max_resorts=max_resorts)

    assert result
    assert result.total_expected == 569  # NOTE fragile!
    # expect more than just the pages we requested, as style sort will grab more
    assert result.total_found > UNTAPPD_BEER_HISTORY_SIZE * max_resorts
    assert not result.found_all
    assert all(r.beer_label_url for r in result.results)


def test_lists(user: User) -> None:
    lists = user.lists()
    assert len(lists) == 13

    result = lists[0]

    assert result.description
    assert result.num_items


def test_lists_detail(
    user: User,
    list_page_1_resp: MockResponse,
    list_page_2_resp: MockResponse,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lists = user.lists()
    fridge = lists[1]  # should be fridge
    monkeypatch.setattr(
        "untappd_scraper.user_lists.list_page_all_sorts",
        lambda _: (list_page_1_resp, list_page_2_resp),
    )  # pyright: ignore[reportCallIssue]
    lists = user.lists_detail(fridge.name)
    assert len(lists) == 1

    result = lists[0]

    assert isinstance(result, WebUserList)
    assert len(result.beers) == result.num_items
    assert result.full_scrape


def test_venue_history(user: User) -> None:
    history = user.venue_history()
    assert len(history) == UNTAPPD_BEER_HISTORY_SIZE

    result = next(iter(history))

    assert result.venue_id
    assert result.first_checkin_id
    assert result.last_checkin_id
