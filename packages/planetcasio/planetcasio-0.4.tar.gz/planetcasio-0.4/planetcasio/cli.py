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
"""Command-line interface definition."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any

import click

from .client import Client
from .programs import ProgramLicense

__all__ = ["cli"]

cli: click.Group
"""Command-line interface for planetcasio.

This command presents various utilities as subcommand, implementing
interactions with Planète Casio.
"""

_client_kwargs_contextvar: ContextVar[dict[str, Any]] = ContextVar(
    "_client_kwargs_contextvar",
)


@contextmanager
def _client_kwargs_context(
    ctx: click.Context,
    base_url: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> Iterator[None]:
    """Place a client kwargs context."""
    kwargs: dict[str, Any] = {}
    if user is not None:
        if password is None:
            ctx.fail("No password provided with the username.")

        kwargs["auth"] = (user, password)
    elif password is not None:
        ctx.fail("No username provided with the password.")

    if base_url is not None:
        kwargs["base_url"] = base_url

    token = _client_kwargs_contextvar.set(kwargs)
    try:
        yield
    finally:
        _client_kwargs_contextvar.reset(token)


@asynccontextmanager
async def _client_context() -> AsyncIterator[Client]:
    """Get a client context for a command-line function."""
    kwargs = _client_kwargs_contextvar.get()
    async with Client(**kwargs) as client:
        yield client


@click.group()  # type: ignore[no-redef]
@click.pass_context
@click.option("-b", "--base-url", help="Base URL to Planète Casio.")
@click.option("-u", "--user", help="Username of the account to use.")
@click.option(
    "-p",
    "--password",
    help="Password of the account to use.",
    hide_input=True,
)
def cli(
    ctx: click.Context,
    base_url: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> None:
    """Command-line interface for planetcasio.

    This command presents various utilities as subcommand, implementing
    interactions with Planète Casio.
    """
    ctx.obj = ctx.with_resource(
        _client_kwargs_context(
            ctx=ctx,
            base_url=base_url,
            user=user,
            password=password,
        ),
    )


async def _update_program(*args, **kwargs) -> None:
    """Update a program."""
    async with _client_context() as client:
        await client.programs.update(*args, **kwargs)


@cli.command()
@click.option(
    "--program-author",
    help="Username or arbitrary text to set as the program's author.",
)
@click.option(
    "--program-version",
    help="Text to set as the program's version.",
)
@click.option(
    "--program-size",
    type=click.IntRange(min=0),
    help="Positive integer to set as the program's size.",
)
@click.option(
    "--program-description",
    help="BBCode text to set as the program's description.",
)
@click.option(
    "--program-license",
    type=ProgramLicense,
    help="Value to set as the program's license.",
)
@click.option(
    "--program-image",
    type=click.Path(path_type=Path),
    help="Path to the image to set as the program's image.",
)
@click.option(
    "--program-file1",
    type=click.Path(path_type=Path),
    help="Path to the file to set as the program's first file.",
)
@click.option(
    "--program-file2",
    type=click.Path(path_type=Path),
    help="Path to the file to set as the program's second file.",
)
@click.option(
    "--program-file3",
    type=click.Path(path_type=Path),
    help="Path to the file to set as the program's third file.",
)
@click.argument("program_id", type=click.IntRange(min=1))
def update_program(
    program_id: int,
    program_author: str | None = None,
    program_version: str | None = None,
    program_size: int | None = None,
    program_description: str | None = None,
    program_license: str | None = None,
    program_image: Path | None = None,
    program_file1: Path | None = None,
    program_file2: Path | None = None,
    program_file3: Path | None = None,
) -> None:
    """Update a program."""
    kwargs: dict[str, Any] = {}
    if program_image is not None:
        kwargs["image"] = program_image
    if program_file1 is not None:
        kwargs["file1"] = program_file1
    if program_file2 is not None:
        kwargs["file2"] = program_file2
    if program_file3 is not None:
        kwargs["file3"] = program_file3

    asyncio.run(
        _update_program(
            program_id,
            author=program_author,
            version=program_version,
            size=program_size,
            description=program_description,
            license_=program_license,
            **kwargs,
        ),
    )
