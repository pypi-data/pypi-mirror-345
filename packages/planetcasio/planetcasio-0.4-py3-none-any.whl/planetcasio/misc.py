#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2024 Thomas Touhey <thomas@touhey.fr>
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
"""Miscellaneous utilities."""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from pydantic import AnyUrl, GetCoreSchemaHandler
from pydantic_core.core_schema import (
    CoreSchema,
    is_instance_schema,
    json_or_python_schema,
    none_schema,
)


class FtpUrl(AnyUrl):
    """FTP URL."""

    __slots__ = ()

    allowed_schemes: ClassVar[set[str]] = {"ftp"}


class StrEnum(str, Enum):
    """String enumeration."""


class NoValueType:
    """Type for the NO_VALUE constant."""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        """Create or return the NO_VALUE constant."""
        try:
            return cls.__unique_value__
        except AttributeError:
            value = super().__new__(cls, *args, **kwargs)
            cls.__unique_value__ = value
            return value

    def __repr__(self):
        return "NO_VALUE"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[NoValueType],
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema.

        This allows the currency type to be handled within pydantic classes,
        and imported/exported in JSON schemas as URNs.

        :param source: The source type.
        """
        return json_or_python_schema(
            json_schema=none_schema(),
            python_schema=is_instance_schema((cls, None)),
        )


NO_VALUE = NoValueType()
