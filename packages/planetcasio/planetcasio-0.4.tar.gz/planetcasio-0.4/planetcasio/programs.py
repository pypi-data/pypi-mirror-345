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
"""Planète Casio's program interactions."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum, IntEnum
from io import BytesIO
from itertools import count
from logging import getLogger
from pathlib import Path
from typing import Annotated

from annotated_types import Ge
from pydantic import AliasChoices, AwareDatetime, BaseModel, Field
from pytz import timezone
from typing_extensions import TypeAliasType

from .bbcode import transform_html_to_bbcode
from .errors import Unauthorized
from .misc import NO_VALUE, NoValueType, StrEnum
from .transport import Feature, FormNotFound, UnexpectedRedirect

ProgramID = TypeAliasType("ProgramID", Annotated[int, Ge(1)])
"""Program identifier.

This represents an integer from 1 onwards.
"""

_PROGRAM_URL_PATTERN = re.compile(r".+?/Fr/programmes/programme(\d+)-")
_SIZE_PATTERN = re.compile(r"(\d+) octets")
_VISITS_PATTERN = re.compile(r"Nombre de visites sur cette page : (\d+)")
_PROGRANK_PATTERN = re.compile(r"Score au progrank : (\d+)")
_PARIS = timezone("Europe/Paris")

logger = getLogger(__name__)


class ProgramCalculator(IntEnum):
    """Targeted calculator for programs."""

    GRAPH_35_100 = 1
    """Graph 35 to 100."""

    GRAPH_25 = 2
    """Graph 25+Pro / 25+E / 25+E II."""

    GRAPH_35 = 3
    """Graph 35+USB / 75(+E) / 85 / 95 SD."""

    GRAPH_100 = 4
    """Graph 100(+)."""

    CLASSPAD_300 = 5
    """ClassPad 300 / 330 (+)."""

    FXCG10 = 6
    """fx-CG 10/20 (Prizm)."""

    CLASSPAD_400 = 7
    """ClassPad 400(+E)."""

    GRAPH_90 = 8
    """Graph 90+E."""

    FX92 = 9
    """fx-92+ SC."""


class ProgramCategory(StrEnum):
    """Program category."""

    GAMES = "a"
    """Games."""

    UTILITIES = "b"
    """Utility programs."""

    CLASSES = "c"
    """Programs for studies."""


class ProgramType(StrEnum):
    """Program type."""

    GAMES_ACTION_SPORT = "a1"
    """Action/sport games."""

    GAMES_SHOOT = "a2"
    """Shooting games."""

    GAMES_PUZZLES = "a3"
    """Puzzle games."""

    GAMES_RPG = "a4"
    """Role-playing games."""

    GAMES_STRATEGY = "a5"
    """Strategy-based games."""

    GAMES_MISC = "a6"
    """Miscellaneous games."""

    GAMES_ADDINS = "a7"
    """Games that come as add-ins."""

    GAMES_PROJECTS = "a8"
    """Game projects."""

    GAMES_CONTEST = "a9"
    """Games made in the context of contests."""

    GAMES_BAZAR = "a10"
    """Bric-a-brac games."""

    GAMES_MLC = "a11"
    """Games made using MLC."""

    GAMES_LUA = "a12"
    """Games made using LuaFX / CGLua."""

    UTILITIES_CONVERSION = "b1"
    """Conversion utilities."""

    UTILITIES_GRAPHICS = "b2"
    """Graphics utilities."""

    UTILITIES_ORGANISERS = "b3"
    """Productive utilities."""

    UTILITIES_MISC = "b4"
    """Miscellaneous utilities."""

    UTILITIES_ADDINS = "b5"
    """Utilities that come as add-ins."""

    UTILITIES_MLC = "b6"
    """Utilities made using MLC."""

    UTILITIES_LUA = "b7"
    """Utilities made using LuaFX / CGLua."""

    CLASSES_MATH = "c1"
    """Math programs."""

    CLASSES_PHYSICS = "c2"
    """Physics programs."""

    CLASSES_CHEMISTRY = "c3"
    """Chemistry programs."""

    CLASSES_ELEC = "c4"
    """Electronics / S.I programs."""

    CLASSES_MISC = "c5"
    """Miscellaneous programs for classes."""

    CLASSES_ADDINS = "c6"
    """Programs for classes that come as add-ins."""


class ProgramFormat(StrEnum):
    """Program format."""

    G1R = "g1r"
    G2R = "g2r"
    G3R = "g3r"
    G1M = "g1m"
    G2M = "g2m"
    G3M = "g3m"
    G1S = "g1s"
    G2S = "g2s"
    G3S = "g3s"
    G1E = "g1e"
    G2E = "g2e"
    G3E = "g3e"
    LUA = "lua"
    ZIP = "zip"
    RAR = "rar"
    TXT = "txt"
    PDF = "pdf"
    FXI = "fxi"
    CAT = "cat"
    LC = "lc"
    MCS = "mcs"
    FLS = "fls"
    CPA = "cpa"
    PY = "py"


class ProgramLicense(StrEnum):
    """Program license."""

    NONE = "none"
    CC_BY = "CC_2.0_BY"
    CC_BY_SA = "CC_2.0_BY-SA"
    CC_BY_NC = "CC_2.0_BY-NC"
    CC_BY_ND = "CC_2.0_BY-ND"
    CC_BY_SA_NC = "CC_2.0_BY-SA-NC"
    CC_BY_NC_ND = "CC_2.0_BY-NC-ND"
    LGPL2 = "LGPL_2.1"
    LGPL3 = "LGPL_3.0"
    GPL2 = "GPL_2.0"
    GPL3 = "GPL_3.0"
    APACHE = "Apache_2.0"
    BSD = "BSD"
    MIT = "MIT_X11"
    ABANDONWARE = "Abandonware"
    CASIO = "Casio_software"
    INCLUDED = "included"
    PUBLIC = "public"


class ProgramOrder(StrEnum):
    """Program order."""

    RELEVANCE = "perti"
    """Sort programs by relevance."""

    AVERAGE = "moy"
    """Sort programs by marks average."""

    MARK_COUNT = "nbrnotes"
    """Sort programs by number of marks."""

    DOWNLOADS = "nbrdl"
    """Sort programs by number of downloads."""

    VISITS = "visites"
    """Sort programs by visits."""

    CREATION_DATE = "date"
    """Sort programs by creation date."""

    LAST_UPDATE_DATE = "datemod"
    """Sort programs by last update date."""

    SIZE = "taille"
    """Sort programs by size."""


class BaseProgram(BaseModel):
    """Base program information."""

    id_: Annotated[
        ProgramID,
        Field(validation_alias=AliasChoices("id", "id_")),
    ]
    """Program identifier."""

    title: str
    """Title."""

    uploader: str
    """User who has uploaded the program."""

    progrank: int
    """Current program rank."""

    has_label: bool
    """Whether the program has the Planète Casio label."""


class Program(BaseProgram):
    """Program-related data."""

    author: str
    """User who has made the program."""

    version: str
    """Version."""

    size: Annotated[int, Ge(0)]
    """Size in bytes."""

    visits: Annotated[int, Ge(0)]
    """Number of visits on the program."""

    created_at: AwareDatetime
    """Date and time of creation."""

    last_updated_at: AwareDatetime
    """Date and time of last update."""

    description: str
    """Description."""


class Programs(Feature):
    """Programs client."""

    __slots__ = ()

    async def get(self, id_: ProgramID, /) -> Program:
        r"""Get details regarding a program.

        :param id\\_: Identifier of the program to get.
        :return: Program.
        :raises NotFound: Program could not be found.
        """
        page = await self.transport.request_html(
            f"Fr/programmes/programme{id_}-1-.html",
        )
        title_el = page.xpath(
            "//span[text()='Version :'][1]/preceding-sibling::span",
        )[0]
        version_el = page.xpath(
            "//span[text()='Version :'][1]/following-sibling::text()[1]",
        )[0]
        size_el = page.xpath(
            "//span[text()='Taille :'][1]/following-sibling::text()[1]",
        )[0]
        created_at_el = page.xpath(
            "//span[text()='Ajouté le :'][1]/following-sibling::text()[1]",
        )[0]
        last_updated_at_el = page.xpath(
            "//span[text()='Modifié le :'][1]/following-sibling::text()[1]",
        )[0]
        misc_el = page.xpath(
            "//text()[contains(., 'Score au progrank')][1]/parent::td",
        )[0]
        uploader_el = page.xpath(
            "//div[@class='profile']//a[contains(@href, 'voir_profil')]",
        )[0]
        author_els = page.xpath(
            "//span[text()='Auteur :']/following-sibling::text()[1]",
        )
        label_els = page.xpath(
            "//img[contains(@onmousemove, 'label de qualité')]",
        )
        desc_el_list = page.xpath(
            "//td/span[text()='Description :'][1]/following-sibling::*",
        )
        for i, el in enumerate(desc_el_list):
            if el.tag == "hr":
                desc_el_list = desc_el_list[:i]
                break

        raw_title = "".join(title_el.itertext()).strip()
        raw_uploader = "".join(uploader_el.itertext()).strip()
        raw_author = str(author_els[0]).strip() if author_els else raw_uploader
        raw_version = str(version_el)
        raw_size = str(size_el)
        raw_created_at = str(created_at_el)
        raw_last_updated_at = str(last_updated_at_el)
        raw_misc = "".join(misc_el.itertext())

        size_match = _SIZE_PATTERN.search(raw_size)
        if size_match is None:
            raise AssertionError(f"Size could not be decoded: {raw_size!r}")

        progrank_match = _PROGRANK_PATTERN.search(raw_misc)
        if progrank_match is None:
            raise AssertionError(
                f"Progrank could not be decoded: {raw_misc!r}",
            )

        visits_match = _VISITS_PATTERN.search(raw_misc)
        if visits_match is None:
            raise AssertionError(f"Visits could not be decoded: {raw_misc}")

        return Program(
            id_=id_,
            title=raw_title.strip(),
            uploader=raw_uploader,
            has_label=len(label_els) > 0,
            author=raw_author,
            version=raw_version.strip(),
            size=int(size_match[1]),
            visits=int(visits_match[1]),
            created_at=datetime.strptime(
                raw_created_at.strip(),
                "%Y-%m-%d %H:%M",
            ).replace(tzinfo=_PARIS),
            last_updated_at=datetime.strptime(
                raw_last_updated_at.strip(),
                "%Y-%m-%d %H:%M",
            ).replace(tzinfo=_PARIS),
            progrank=int(progrank_match[1]),
            description=transform_html_to_bbcode(desc_el_list),
        )

    async def search(
        self,
        /,
        *,
        calculator: ProgramCalculator | str | int | None = None,
        category: ProgramCategory | str | None = None,
        type_: ProgramType | str | None = None,
        formats: set[ProgramFormat | str] | None = None,
        with_label: bool | None = None,
        order: ProgramOrder | str = ProgramOrder.RELEVANCE,
    ) -> AsyncIterator[BaseProgram]:
        """Search for programs.

        :param calculator: Targeted calculators to filter on.
        :param category: Program category to filter on.
        :param type: Program type to filter on.
        :param formats: Program formats to filter on.
        :param with_label: Whether filtered programs have a label.
        :param order: Sorting order of the returned results.
        :return: Program iterator.
        """
        params: dict[str, str] = {"nbrPrgmPage": "200"}
        if isinstance(order, Enum):
            params["tri"] = str(order.value)
        else:
            params["tri"] = str(order)
        if isinstance(calculator, Enum):
            params["calc"] = str(calculator.value)
        elif calculator is not None:
            params["calc"] = str(calculator)
        if isinstance(category, Enum):
            params["categorie"] = str(category.value)
        elif category is not None:
            params["categorie"] = str(category)
        if isinstance(type_, Enum):
            params["type"] = str(type_.value)
        elif type_ is not None:
            params["type"] = str(type_)
        if with_label is True:
            params["label"] = "oui"
        elif with_label is False:
            params["label"] = "non"
        if formats is not None:
            raw_formats = {
                str(x.value) if isinstance(x, Enum) else str(x)
                for x in formats
            }
            if not raw_formats:
                return
            for fmt in raw_formats:
                params[f"format[{fmt}]"] = "on"

        for pageno in count(start=1):
            page = await self.transport.request_html(
                "Fr/programmes/trier_programmes.php",
                params={"page": str(pageno), **params},
            )

            at_least_one_el = False
            for el in page.xpath("//div[@class='triPrgmNrml']"):
                at_least_one_el = True
                title_el = el.xpath(".//div[@class='donnees']/a[1]")[0]
                author_el = el.xpath(
                    ".//div[@class='donnees']/span[text()='Posteur : ']"
                    + "/following-sibling::text()[1]",
                )[0]
                score_el = el.xpath(
                    ".//div[@class='donnees']/span[text()='Score : ']"
                    + "/following-sibling::text()[1]",
                )[0]
                label_els = el.xpath(
                    ".//img[contains(@onmousemove, 'label Planète Casio')]",
                )

                raw_url = title_el.attrib["href"].strip()
                raw_title = "".join(title_el.itertext()).strip()
                raw_author = str(author_el).strip()
                raw_score = str(score_el).strip()

                id_match = _PROGRAM_URL_PATTERN.search(raw_url)
                if id_match is None:
                    raise AssertionError(
                        f"Could not find program id in link: {raw_url}",
                    )

                yield BaseProgram(
                    id=int(id_match[1]),
                    title=raw_title,
                    uploader=raw_author,
                    progrank=int(raw_score),
                    has_label=len(label_els) > 0,
                )

            # Sometimes the pagination is off, i.e. pages are displayed but
            # are in reality empty. In this case, we want to stop requesting
            # pages.
            if not at_least_one_el:
                return

            # Get the pagination on the result.
            last_page_el = page.xpath(
                "//p[contains(., 'Pages :')][1]/*[last()]",
            )[0]
            if pageno >= int(last_page_el.text):
                break

    async def update(
        self,
        id_: ProgramID,
        /,
        *,
        author: str | None = None,
        version: str | None = None,
        size: int | None = None,
        description: str | None = None,
        license_: ProgramLicense | None = None,
        image: Path
        | tuple[Path | str, BytesIO | bytes]
        | NoValueType = NO_VALUE,
        file1: Path
        | tuple[Path | str, BytesIO | str | bytes]
        | NoValueType = NO_VALUE,
        file2: Path
        | tuple[Path | str, BytesIO | str | bytes]
        | NoValueType = NO_VALUE,
        file3: Path
        | tuple[Path | str, BytesIO | str | bytes]
        | NoValueType = NO_VALUE,
    ) -> None:
        r"""Update a program with a given identifier.

        .. note::

            One can only replace a file or image on a program on Planète Casio,
            not remove it.

        :param id\_: Identifier of the program to update.
        :param author: New author to define on the program.
        :param version: New version to define on the program.
        :param size: New size to define on the program.
        :param description: New description to define on the program.
        :param license\_: New license to define on the program.
        :param image: New image to define on the program.
        :param file1: File to add or replace in the first slot, with the path
            or file name and contents.
        :param file2: File to add or replace in the second slot, with the path
            or file name and contents.
        :param file3: File to add or replace in the third slot, with the path
            or file name and contents.
        :raises Unauthorized: The operation was unauthorized.
        """
        values: dict[str, str] = {}
        files: dict[
            str,
            Path | str | tuple[Path | str, BytesIO | str | bytes],
        ] = {}
        if author is not None:
            values["auteur"] = author
        if version is not None:
            values["version"] = version
        if size is not None:
            values["taille"] = str(size)
        if description is not None:
            values["description"] = description
        if license is not None:
            values["licence"] = str(license_)
        if not isinstance(image, NoValueType):
            files["image"] = image
        if not isinstance(file1, NoValueType):
            files["fichier1"] = file1
        if not isinstance(file2, NoValueType):
            files["fichier2"] = file2
        if not isinstance(file3, NoValueType):
            files["fichier3"] = file3

        try:
            async with self.transport.submit_form(
                "Fr/programmes/modif_programme.php",
                values,
                params={"id": str(id_)},
                form_path="//form[@name='modif']",
                files=files,
            ):
                pass
        except UnexpectedRedirect as exc:
            # The modification form was accessed anonymously, which does not
            # work.
            if exc.location == f"{self.transport.config.base_url}Fr/compte":
                raise Unauthorized() from exc

            raise
        except FormNotFound as exc:
            # The modification form was accessed as an account that does not
            # have access to it.
            raise Unauthorized() from exc
