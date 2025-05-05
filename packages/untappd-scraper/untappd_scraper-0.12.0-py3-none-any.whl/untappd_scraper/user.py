"""Untappd user functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from utpd_models_web.user import WebUserDetails

from untappd_scraper.beer import checkin_activity
from untappd_scraper.html_session import get
from untappd_scraper.logging_config import configure_logging, logger
from untappd_scraper.user_beer_history import (
    UserHistoryResponse,
    beer_history,
    brewery_history,
)
from untappd_scraper.user_lists import WebUserList, load_user_lists, scrape_list_beers
from untappd_scraper.user_venue_history import load_user_venue_history
from untappd_scraper.web import url_of

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection

    from requests_html import HTMLResponse
    from utpd_models_web.checkin import WebActivityBeer
    from utpd_models_web.venue import WebUserHistoryVenue

configure_logging(__name__)

logger.info("Loading user...")


@dataclass
class User:
    """Untappd user."""

    user_id: str
    user_name: str = field(init=False)

    _page: HTMLResponse = field(init=False, repr=False)
    user_details: WebUserDetails = field(init=False, repr=False)

    _activity_details: tuple[WebActivityBeer, ...] | None = field(
        default=None, init=False, repr=False
    )
    _lists: list[WebUserList] = field(default_factory=list, init=False, repr=False)
    _venue_history: list[WebUserHistoryVenue] = field(
        default_factory=list, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Post-init method to load user details."""
        self._page = get(url_of(self.user_id))  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
        if not self._page.ok:
            msg = f"Invalid userid {self.user_id} ({self._page})"
            raise ValueError(msg)

        self.user_details = user_details(resp=self._page)
        self.user_name = self.user_details.name

    def activity(self) -> tuple[WebActivityBeer, ...]:
        """Return a user's recent checkins.

        Returns:
            tuple[WebActivityBeer]: last 5 (or so) checkins
        """
        if self._activity_details is None:
            self._activity_details = tuple(checkin_activity(self._page))

        return self._activity_details

    def beer_history(self) -> UserHistoryResponse:
        """Scrape last 25 (or so) of a user's uniques.

        Returns:
            UserHistoryResponse: user's recent uniques
        """
        return beer_history(self.user_id)

    def brewery_history(self, brewery_id: int, max_resorts: int = 0) -> UserHistoryResponse:
        """Scrape as many of a user's uniques as possible from a brewery.

        Args:
            brewery_id (int): brewery id to filter by
            max_resorts (NumReSorts): number of times to re-sort the list to get more uniques

        Returns:
            UserHistoryResponse: user's uniques
        """
        return brewery_history(
            user_id=self.user_id, brewery_id=brewery_id, max_resorts=max_resorts
        )

    def lists(self) -> list[WebUserList]:
        """Scrape user's list page and return all visible listed beers.

        Returns:
            Collection[WebUserList]: all user's lists with 15 (or so) visible beers
        """
        if not self._lists:
            self._lists = load_user_lists(self.user_id)

        return self._lists

    def lists_detail(self, list_name: str) -> list[WebUserList]:
        """Return populated details of a user's list.

        Args:
            list_name (str): list name (or part thereof, case-insensitive)

        Returns:
            list[WebUserList]: matching lists with detail filled in
        """
        matching = [
            user_list
            for user_list in self.lists()
            if list_name.casefold() in user_list.name.casefold()
        ]

        for user_list in matching:
            user_list.beers.update(scrape_list_beers(user_list))

        return matching

    def venue_history(self) -> Collection[WebUserHistoryVenue]:
        """Scrape last 25 (or so) of a user's visited venues.

        Returns:
            Collection[WebUserHistoryVenue]: user's recent venues
        """
        if not self._venue_history:
            self._venue_history = load_user_venue_history(self.user_id)

        return self._venue_history

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Return unknown attributes from user details.

        Args:
            name (str): attribute to lookup

        Returns:
            Any: attribute value
        """
        return getattr(self.user_details, name)


# ----- user details processing -----


def user_details(resp: HTMLResponse) -> WebUserDetails:
    """Parse a user's main page into user details.

    Args:
        resp (HTMLResponse): user's main page loaded

    Returns:
        WebUserDetails: general user details
    """
    user_info_el = resp.html.find(".user-info .info", first=True)
    user_name = user_info_el.find("h1", first=True).text.strip()  # pyright: ignore[reportAttributeAccessIssue]
    user_id = user_info_el.find(".user-details p.username", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    user_location = user_info_el.find(".user-details p.location", first=True).text  # pyright: ignore[reportAttributeAccessIssue]

    stats_el = user_info_el.find(".stats", first=True)  # pyright: ignore[reportAttributeAccessIssue]
    total_beers = stats_el.find('[data-href=":stats/general"] span', first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    total_uniques = stats_el.find('[data-href=":stats/beerhistory"] span', first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    total_badges = stats_el.find('[data-href=":stats/badges"] span', first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    total_friends = stats_el.find('[data-href=":stats/friends"] span', first=True).text  # pyright: ignore[reportAttributeAccessIssue]

    return WebUserDetails(
        user_id=user_id,
        name=user_name,
        location=user_location,
        url=user_info_el.url,  # pyright: ignore[reportAttributeAccessIssue]
        total_beers=str_to_int(total_beers),
        total_uniques=str_to_int(total_uniques),
        total_badges=str_to_int(total_badges),
        total_friends=str_to_int(total_friends),
    )


def str_to_int(numeric_string: str) -> int:
    """Convert a string to an integer.

    Args:
        numeric_string (str): amount with commas

    Returns:
        int: value as an integer
    """
    return int(numeric_string.replace(",", ""))
