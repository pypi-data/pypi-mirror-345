#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2024-2025 Thomas Touhey <thomas@touhey.fr>
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
"""Planète Casio client."""

from __future__ import annotations

from .account import Account
from .programs import Programs
from .shout import Shout
from .transport import BaseClient, TransportConfig
from .user_profiles import UserProfiles


class Client(BaseClient):
    """Client for interacting with Planète Casio.

    :param base_url: Base URL to access Planète Casio.
    :param auth: Credentials to use to access authenticated operations.
        If :py:data:`None` (*by default*), operations will be made
        anonymously.
    """

    __slots__ = ("account", "programs", "shout", "user_profiles")

    account: Account
    """Account-related operations."""

    user_profiles: UserProfiles
    """User profiles related operations."""

    programs: Programs
    """Programs-related operations."""

    shout: Shout
    """Shoutbox-related operations."""

    def __init__(
        self,
        /,
        *,
        base_url: str = "https://www.planet-casio.com/",
        auth: tuple[str, str] | None = None,
    ) -> None:
        BaseClient.__init__(
            self,
            TransportConfig(base_url=base_url, auth=auth),
        )
        self.account = Account(self)
        self.programs = Programs(self)
        self.shout = Shout(self)
        self.user_profiles = UserProfiles(self)
