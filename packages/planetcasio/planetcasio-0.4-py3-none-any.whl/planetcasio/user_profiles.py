#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2025 Thomas Touhey <thomas@touhey.fr>
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use, modify
# and/or redistribute the software under the terms of the CeCILL-C license
# as circulated by CEA, CNRS and INRIA at the following
# URL: https://cecill.info
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean
# that it is complicated to manipulate, and that also therefore means that it
# is reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.
# *****************************************************************************
"""Planète Casio's user profile interactions."""

from __future__ import annotations

import re
from datetime import date, datetime

from dateparser import parse as parse_datetime
from pydantic import AwareDatetime, BaseModel, HttpUrl
from pytz import timezone

from .bbcode import transform_html_to_bbcode
from .misc import FtpUrl
from .transport import Feature, Username

_POINTS_PATTERN = re.compile(r"Points\s*: ([0-9]+)")
_CHALLENGES_PATTERN = re.compile(r"Défis\s*: ([0-9]+)")
_PARIS = timezone("Europe/Paris")


class UserProfile(BaseModel):
    """User profile."""

    username: Username
    """Username."""

    is_online: bool
    """Whether the member is online or not."""

    points: int
    """Number of points."""

    completed_challenges: int
    """Number of completed challenges."""

    registration_date: date
    """Registration date."""

    last_login_date: AwareDatetime | None
    """Last login date."""

    personal_website_url: HttpUrl | FtpUrl | None
    """Personal website."""

    presentation: str
    """Presentation, in BBCode."""

    signature: str
    """Signature, in BBCode."""


class UserProfiles(Feature):
    """User profile client."""

    __slots__ = ()

    async def get(self, username: Username, /) -> UserProfile:
        """Get a user profile from a username.

        :param username: Username for which to get the user profile.
        :return: Obtained user profile.
        :raises NotFound: User profile could not be found.
        """
        page = await self.transport.request_html(
            "Fr/compte/voir_profil.php",
            params={"membre": username.casefold()},
        )

        username_el = page.xpath(
            "//a[contains(concat(' ', @class, ' '), ' profile-name ')]",
        )[0]
        online_el = page.xpath(
            "//span[contains(concat(' ', @class, ' '), ' profile-online ')]",
        )[0]
        points_el = page.xpath(
            "//span[contains(concat(' ', @class, ' '), ' profile-points ')]",
        )[0]
        challenges_el = page.xpath(
            "//span[contains(concat(' ', @class, ' '), ' profile-chpoints ')]",
        )[0]
        registration_date_el = page.xpath(
            '//span[contains(text(), "Date d\'inscription")]'
            + "/following-sibling::text()[1]",
        )[0]
        last_login_date_el = page.xpath(
            '//span[contains(text(), "Date de derniere connexion")]'
            + "/following-sibling::text()[1]",
        )[0]
        website_els = page.xpath(
            "//span[contains(text(), 'Site Perso')]/following-sibling::a[1]",
        )
        presentation_els = page.xpath(
            "//p[text() = 'Présentation :'][1]/following-sibling::*",
        )

        points_match = _POINTS_PATTERN.search(points_el.text)
        if points_match is None:
            raise ValueError(
                f"Points could not be extracted: {points_el.text!r}",
            )

        completed_challenges_match = _CHALLENGES_PATTERN.search(
            challenges_el.text,
        )
        if completed_challenges_match is None:
            raise ValueError(
                "Completed challenges could not be extracted: "
                f"{challenges_el.text!r}",
            )

        raw_registration_date = str(registration_date_el).strip()
        registration_date = parse_datetime(
            raw_registration_date,
            languages=["fr"],
        )
        if registration_date is None:
            raise ValueError(
                "Registration date could not be parsed: "
                f"{raw_registration_date!r}",
            )

        raw_last_login_date = str(last_login_date_el).strip()
        if raw_last_login_date == "Jamais":
            last_login_date: datetime | None = None
        else:
            last_login_date = parse_datetime(
                raw_last_login_date,
                languages=["fr"],
            )
            if last_login_date is None:
                raise ValueError(
                    "Last login date could not be parsed: "
                    f"{last_login_date!r}",
                )

            last_login_date = last_login_date.replace(tzinfo=_PARIS)

        website = None
        for website_el in website_els:
            website = website_el.get("href")

        # There are two sections next to each other at the same level,
        # "Présentation" and "Signature". We need to distinguish between
        # both.
        #
        # While presentation contents is not within a div, signature contents
        # is within a div with class "signature". It is preceded by a <p>
        # with contents "Signature :", and an hr, which we want to remove.
        _i = 0
        for _i, el in enumerate(presentation_els[2:], start=2):
            if el.tag == "div" and el.get("class") == "signature":
                break
        else:
            raise ValueError("Could not find a signature!")

        signature_els = list(presentation_els[_i])
        presentation_els = presentation_els[: _i - 2]

        return UserProfile(
            username=username_el.text,
            is_online=online_el.text == "En ligne",
            points=int(points_match[1]),
            completed_challenges=int(completed_challenges_match[1]),
            registration_date=registration_date.replace(tzinfo=_PARIS),
            last_login_date=last_login_date,
            personal_website_url=website,
            presentation=transform_html_to_bbcode(presentation_els),
            signature=transform_html_to_bbcode(signature_els),
        )
