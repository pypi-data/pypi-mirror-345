"""Web-scraper user details."""

from __future__ import annotations

from functools import total_ordering

from pydantic.dataclasses import dataclass

from utpd_models_web.injector import eq_by, hash_by, lt_by


@total_ordering
@dataclass(frozen=True)
class WebUserDetails:
    """A user's details from the user's web page."""

    user_id: str
    name: str
    location: str
    url: str
    total_beers: int
    total_uniques: int
    total_badges: int
    total_friends: int

    __eq__ = eq_by("user_id")
    __lt__ = lt_by("user_id")
    __hash__ = hash_by("user_id")  # pyright: ignore[reportAssignmentType]
