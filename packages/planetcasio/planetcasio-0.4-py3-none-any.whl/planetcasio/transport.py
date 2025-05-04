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
"""Planète Casio transport."""

from __future__ import annotations

from asyncio import Lock
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO, IOBase
from logging import getLogger
from pathlib import Path
from time import monotonic
from types import SimpleNamespace, TracebackType
from typing import Annotated, Any, TypeVar, overload
from urllib.parse import urljoin

from aiohttp import (
    ClientResponse,
    ClientResponseError,
    ClientSession,
    FormData,
    TraceConfig,
    TraceRequestEndParams,
    TraceRequestStartParams,
)
from lxml.etree import Element
from lxml.html.html5parser import HTMLParser, fromstring
from pydantic import (
    BaseModel,
    HttpUrl,
    StringConstraints,
    TypeAdapter,
    model_validator,
)
from typing_extensions import TypeAliasType

from .errors import (
    CredentialsRequired,
    InvalidCredentials,
    NotFound,
    Unauthorized,
)

TransportT = TypeVar("TransportT", bound="Transport")
APIResponseT = TypeVar("APIResponseT", bound=BaseModel)
BaseClientT = TypeVar("BaseClientT", bound="BaseClient")

Username = TypeAliasType(
    "Username",
    Annotated[
        str,
        StringConstraints(pattern=r"^[A-Za-z0-9]+$"),
    ],
)
"""Username type, as a string type containing latin letters and digits.

Note that usernames on Planète Casio are case-insensitive.
"""

Password = TypeAliasType(
    "Password",
    Annotated[str, StringConstraints(pattern=r"^.+$")],
)
"""Password type, as a string type with at least one character."""

logger = getLogger(__name__)


class UnexpectedRedirect(Exception):
    """A 3xx status code was received while redirects were disabled."""

    __slots__ = ("location",)

    location: str | None
    """Location to which the request was originally redirected."""

    def __init__(
        self,
        message: str | None = None,
        /,
        *,
        location: str | None = None,
    ) -> None:
        if not message:
            message = "Unexpected redirect"
            if location:
                message += f" to: {location}"

        super().__init__(message)
        self.location = location


class FormNotFound(Exception):
    """Form was not found with the given parameters."""

    __slots__ = ()

    def __init__(self, message: str | None = None, /) -> None:
        super().__init__(message or "Form not found")


class _AuthData(BaseModel):
    """Current authentication data."""

    cookie: str | None = None
    """Cookie, if need be to export it."""

    expires_at: datetime | None = None
    """Expiration date and time for the authentication."""


class TransportConfig(BaseModel):
    """Transport configuration."""

    base_url: HttpUrl
    """Base URL."""

    auth: tuple[Username, Password] | None
    """Optional redentials."""

    @model_validator(mode="after")
    def _validate(self, /) -> TransportConfig:
        """Validate the configuration."""
        if not self.base_url.path.endswith("/"):
            self.base_url.path += "/"

        return self


class Transport:
    """Client for interacting with Planète Casio."""

    __slots__ = (
        "_auth_data",
        "_auth_lock",
        "config",
        "session",
    )

    _auth_data: _AuthData | None
    """Current authentication data."""

    _auth_lock: Lock
    """Authentication lock."""

    config: TransportConfig
    """Configuration."""

    session: ClientSession
    """HTTP client session."""

    def __init__(
        self,
        /,
        *,
        session: ClientSession,
        config: TransportConfig,
    ) -> None:
        self._auth_data = None
        self._auth_lock = Lock()
        self.config = config
        self.session = session

        trace_config = TraceConfig()
        trace_config.on_request_start.append(self._on_request_start)
        trace_config.on_request_end.append(self._on_request_end)
        trace_config.freeze()
        self.session.trace_configs.append(trace_config)

    @classmethod
    @asynccontextmanager
    async def context(
        cls: type[TransportT],
        config: TransportConfig,
        /,
    ) -> AsyncIterator[TransportT]:
        """Get a transport in a context."""
        async with ClientSession(raise_for_status=True) as session:
            yield cls(session=session, config=config)

    async def _on_request_start(
        self,
        session: ClientSession,
        context: SimpleNamespace,
        params: TraceRequestStartParams,
        /,
    ) -> None:
        """Initialize a trace for a provided HTTP request.

        :param session: Session on which the request is started.
        :param context: Context in which to store data.
        :param params: Request parameters.
        """
        context.start = monotonic()

    async def _on_request_end(
        self,
        session: ClientSession,
        context: SimpleNamespace,
        params: TraceRequestEndParams,
        /,
    ) -> None:
        """End a trace for a provided HTTP request.

        :param session: Session on which the request is ended.
        :param context: Context from which to retrieve data.
        :param params: Request parameters.
        """
        logger.info(
            "%s %s %03d %.02fs",
            params.method,
            params.url,
            params.response.status,
            monotonic() - context.start,
        )

    @asynccontextmanager
    async def _request(
        self,
        path: str,
        /,
        *,
        method: str | None = None,
        params: dict[str, str] | None = None,
        json_data: Any = None,
        form_data: Any = None,
        allow_redirects: bool = False,
    ) -> AsyncIterator[ClientResponse]:
        """Make a request to the website.

        :param path: Path to the endpoint to request.
        :param method: Method to use with the endpoint.
        :param params: Query parameters to pass to the API endpoint.
        :param json_data: JSON data to pass in the request body.
        :param form_data: Form to pass in the request body.
        :param allow_redirects: Whether to allow redirects.
        :return: Obtained response.
        """
        headers: dict[str, str] = {}
        json: dict[str, Any] | None = None
        data: dict[str, str] | None = None
        if json_data is not None:
            if form_data is not None:
                raise ValueError("Either JSON or form data is expected.")

            json = json_data
            method = "POST"
        elif form_data is not None:
            data = form_data
            method = "POST"
        else:
            method = "GET"

        try:
            async with self.session.request(
                method,
                urljoin(str(self.config.base_url), path),
                params=params,
                data=data,
                json=json,
                headers=headers,
                allow_redirects=allow_redirects,
            ) as response:
                if response.status in range(300, 400) and not allow_redirects:
                    raise UnexpectedRedirect(
                        location=response.headers.get("location"),
                    )

                yield response
        except ClientResponseError as exc:
            if exc.status == 404:
                raise NotFound() from exc

            raise

    async def _parse_html_from_response(
        self,
        response: ClientResponse,
        /,
    ) -> Element:
        """Parse HTML provided in a client response.

        :param response: Response from which to parse the HTML content.
        :return: Top-level element of the HTML content.
        """
        return fromstring(
            await response.text(),
            parser=HTMLParser(namespaceHTMLElements=False),
        )

    def _make_form_data(
        self,
        /,
        *,
        data: dict[str, str],
        files: dict[
            str,
            Path | str | tuple[str | Path, BytesIO | bytes | str],
        ],
    ) -> FormData:
        """Make form data out of the provided simple and file data.

        :param data: Simple data, i.e. textual values.
        :param files: File data.
        :return: Constructed file data.
        """
        form_data = FormData()
        for key, value in data.items():
            form_data.add_field(key, value)

        for key, file_value in files.items():
            if isinstance(file_value, (Path, str)):
                file_path: Path | str = file_value
                file_contents: IOBase = open(file_value, "rb")
            else:
                file_path, raw_file_contents = file_value
                if isinstance(raw_file_contents, str):
                    file_contents = BytesIO(raw_file_contents.encode("utf-8"))
                elif isinstance(raw_file_contents, bytes):
                    file_contents = BytesIO(raw_file_contents)
                else:
                    file_contents = raw_file_contents

            form_data.add_field(
                key,
                file_contents,
                filename=file_path.name
                if isinstance(file_path, Path)
                else file_path.rpartition("/")[2].rpartition("\\")[2],
            )

        return form_data

    @asynccontextmanager
    async def _submit_form(
        self,
        path: str,
        values: dict[str, str] | None = None,
        /,
        *,
        form_path: str = "//form",
        params: dict[str, str] | None = None,
        files: dict[str, Path | str | tuple[str | Path, BytesIO | bytes | str]]
        | None = None,
    ) -> AsyncIterator[ClientResponse]:
        """Submit an HTML form present on the website.

        :param path: Path to the page containing the form to submit.
        :param values: Values to add to the form.
        :param form_path: XPath of the form to submit.
        :param params: Query parameters to get the form.
        :param files: File values to add to the form.
        """
        async with self._request(path, params=params) as response:
            html = await self._parse_html_from_response(response)
            for form in html.xpath(form_path):
                data: dict[str, str] = {}
                file_data: dict[
                    str,
                    Path | str | tuple[str | Path, BytesIO | bytes | str],
                ] = {}
                missing: set[str] = set()

                for inp in form.xpath(".//input"):
                    name = inp.get("name")
                    if not name:
                        continue

                    if values is not None and name in values:
                        data[name] = values.pop(name) or ""
                        continue

                    inp_type = inp.get("type", "text")
                    if inp_type in ("checkbox", "radio"):
                        data[name] = (
                            "on"
                            if inp.get("checked")
                            in (
                                None,
                                "",
                                "checked",
                            )
                            else ""
                        )
                        continue

                    if inp_type in ("text", "hidden"):
                        data[name] = inp.attrib.get("value") or ""
                        continue

                    if inp_type == "file":
                        if files is not None and name in files:
                            file_data[name] = files.pop(name)
                            continue

                        file_data[name] = ("", b"")
                        continue

                    missing.add(name)

                for inp in form.xpath(".//textarea"):
                    name = inp.get("name")
                    if not name:
                        continue

                    if values is not None and name in values:
                        data[name] = values.pop(name) or ""
                        continue

                    data[name] = "".join(inp.itertext())

                for inp in form.xpath(".//select"):
                    name = inp.get("name")
                    if not name:
                        continue

                    default_value: str | None = None
                    selvalue: str | None = None
                    for opt in inp.xpath(".//option"):
                        optvalue = opt.attrib.get("value", opt.text) or ""
                        optsel = opt.attrib.get("selected") == "selected"

                        if optsel:
                            selvalue = optvalue
                            break

                        if default_value is None:
                            default_value = optvalue

                    if selvalue is None:
                        if default_value is not None:
                            data[name] = default_value
                    else:
                        data[name] = selvalue

                    continue

                if missing:
                    raise ValueError(
                        "Missing fields: " + ", ".join(sorted(missing)),
                    )

                # Add the additional items from the provided values.
                if values is not None:
                    for name, value in values.items():
                        data[name] = value

                common_keys = set(data).intersection(file_data)
                if common_keys:
                    raise ValueError(
                        f"Fields in both data and file data: {common_keys}",
                    )

                final_data = self._make_form_data(data=data, files=file_data)

                async with self.session.request(
                    "POST",
                    form.get("action") or response.url,
                    data=final_data,
                    allow_redirects=False,
                ) as form_response:
                    yield form_response

                break
            else:
                raise FormNotFound()

    async def authenticate(self, /) -> _AuthData:
        """Authenticate to the API."""
        data = self._auth_data
        if data is not None and (
            data.expires_at is None
            or data.expires_at > datetime.now(timezone.utc)
        ):
            return data

        async with self._auth_lock:
            data = self._auth_data
            if data is not None and (
                data.expires_at is None
                or data.expires_at > datetime.now(timezone.utc)
            ):
                return data

            auth: tuple[str, str] | None = self.config.auth
            if auth is None:
                data = self._auth_data = _AuthData()
                return data

            username, password = auth
            async with self._submit_form(
                "Fr/compte",
                {
                    "username": username,
                    "password": password,
                    "redirection": f"{self.config.base_url}Fr",
                },
                form_path='//form[@role="form"]',
            ) as response:
                if (
                    response.status != 302
                    or response.headers["Location"]
                    != f"{self.config.base_url}Fr"
                ):
                    raise InvalidCredentials()

                cookies = self.session.cookie_jar.filter_cookies(
                    str(self.config.base_url),
                )
                cookie = cookies["planete_casio_session"]
                data = self._auth_data = _AuthData(cookie=cookie.value)
                return data

    async def check_auth(self, /) -> None:
        """Check that we have valid authentication data.

        :raises CredentialsRequired: Credentials have not been provided.
        """
        if self.config.auth is None:
            raise CredentialsRequired()

    async def get_cookie(self, /) -> str:
        """Get the current session cookie.

        :return: Current cookie.
        """
        await self.check_auth()
        data = await self.authenticate()
        if data.cookie is None:  # pragma: no cover
            raise CredentialsRequired()

        return data.cookie

    @overload
    async def request_api(
        self,
        path: str,
        /,
        *,
        model: None = None,
        method: str | None = None,
        params: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> None: ...

    @overload
    async def request_api(
        self,
        path: str,
        /,
        *,
        model: type[APIResponseT],
        method: str | None = None,
        params: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> APIResponseT: ...

    async def request_api(
        self,
        path: str,
        /,
        *,
        model: type[APIResponseT] | None = None,
        method: str | None = None,
        params: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> APIResponseT | None:
        """Make an API request, and expect JSON to be returned.

        :param path: Path to the API endpoint.
        :param method: Method to use with the API endpoint.
        :param params: Query parameters to pass to the API endpoint.
        :param form_data: Form data to post to the endpoint.
        :param model: Expected response model.
        :return: API response, in the provided format.
        """
        await self.authenticate()
        try:
            async with self._request(
                path,
                method=method,
                params=params,
                form_data=form_data,
            ) as response:
                if model is None:
                    return None

                return TypeAdapter(model).validate_python(
                    await response.json(),
                )
        except ClientResponseError as exc:
            if exc.status == 401:
                raise Unauthorized() from exc

            raise

    async def request_html(
        self,
        path: str,
        /,
        *,
        params: dict[str, str] | None = None,
    ) -> Element:
        """Make a web interface request, and expect HTML to be returned.

        :param path: Path to the web interface endpoint.
        :param query: Query parameters.
        :return: Parsed document.
        """
        await self.authenticate()
        async with self._request(
            path,
            params=params,
            allow_redirects=True,
        ) as response:
            return await self._parse_html_from_response(
                response,
            )

    @asynccontextmanager
    async def submit_form(
        self,
        path: str,
        values: dict[str, str] | None = None,
        /,
        *,
        form_path: str = "//form",
        params: dict[str, str] | None = None,
        files: dict[str, Path | str | tuple[str | Path, BytesIO | bytes | str]]
        | None = None,
    ) -> AsyncIterator[ClientResponse]:
        """Submit an HTML form present on the website.

        :param path: Path to the page containing the form to submit.
        :param values: Values to add to the form.
        :param form_path: XPath of the form to submit.
        :param params: Query parameters to get the form.
        :param files: File values to add to the form.
        """
        await self.authenticate()
        async with self._submit_form(
            path,
            values,
            form_path=form_path,
            params=params,
            files=files,
        ) as response:
            yield response


class BaseClient:
    """Holder for a transport, which creates the transport if need be."""

    __slots__ = (
        "_config",
        "_transport",
        "_transport_context",
        "_transport_depth",
        "_transport_lock",
    )

    _config: TransportConfig
    """Configuration to apply to the transport."""

    _transport: Transport | None
    """Current transport."""

    _transport_context: AbstractAsyncContextManager | None
    """Current transport context."""

    _transport_depth: int
    """Current depth of the transport context."""

    _transport_lock: Lock
    """Lock for handling the transport."""

    @property
    def transport(self, /) -> Transport:
        """Get the current transport."""
        transport = self._transport
        if transport is None:
            raise RuntimeError("No transport available in this context.")

        return transport

    def __init__(self, config: TransportConfig, /) -> None:
        self._config = config
        self._transport = None
        self._transport_context = None
        self._transport_depth = 0
        self._transport_lock = Lock()

    async def __aenter__(self: BaseClientT) -> BaseClientT:
        await self._push_transport()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return await self._pop_transport(exc_type, exc, traceback)

    async def _push_transport(self, /) -> None:
        """Create a new transport."""
        async with self._transport_lock:
            self._transport_depth += 1
            if self._transport is None:
                context = Transport.context(self._config)
                self._transport_context = context
                self._transport = await context.__aenter__()

    async def _pop_transport(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool | None:
        """Pop the current transport."""
        async with self._transport_lock:
            depth = self._transport_depth
            context = self._transport_context
            if depth < 1 or context is None:
                raise RuntimeError("No transport available to pop.")

            self._transport_depth = depth = depth - 1
            catch_exc: bool | None = None
            if depth < 1:
                try:
                    catch_exc = await context.__aexit__(
                        exc_type,
                        exc,
                        traceback,
                    )
                finally:
                    self._transport_context = None
                    self._transport = None

        return catch_exc


class Feature:
    """Object that makes use of a base client."""

    __slots__ = ("client",)

    client: BaseClient
    """Client to make use of."""

    def __init__(self, client: BaseClient, /) -> None:
        self.client = client

    @property
    def transport(self, /) -> Transport:
        """Get the transport."""
        return self.client.transport
