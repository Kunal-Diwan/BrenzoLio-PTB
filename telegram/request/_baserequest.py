#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an abstract class to make POST and GET requests."""
import abc
from contextlib import AbstractAsyncContextManager
from http import HTTPStatus
from types import TracebackType
from typing import Union, Tuple, Type, Optional, ClassVar

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]

from telegram._version import __version__ as ptb_ver
from telegram.request import RequestData

from telegram.error import (
    TelegramError,
    BadRequest,
    ChatMigrated,
    Conflict,
    InvalidToken,
    NetworkError,
    RetryAfter,
    Forbidden,
)
from telegram._utils.types import JSONDict


class BaseRequest(
    AbstractAsyncContextManager,
    abc.ABC,
):
    """Abstract interface class that allows python-telegram-bot to make requests to the Bot API.
    Can be implemented via different asyncio HTTP libraries. An implementation of this class
    must implement all abstract methods and properties. In addition, :attr:`connection_pool_size`
    can optionally be overridden.

    Instances of this class can be used as asyncio context managers, where

    .. code:: python

        async with request_object:
            # code

    is roughly equivalent to

    .. code:: python

        try:
            request_object.initialize()
            # code
        finally:
            request_object.stop()
    """

    __slots__ = ()

    USER_AGENT: ClassVar[str] = f'python-telegram-bot v{ptb_ver} (https://python-telegram-bot.org)'
    """:obj:`str`: A description that can be used as user agent for requests made to the Bot API.
    """

    @property
    def connection_pool_size(self) -> int:
        """Implement this method to allow PTB to infer the size of the connection pool. By default
        just raises :exc:`NotImplementedError`.
        """
        raise NotImplementedError

    async def __aenter__(self) -> 'BaseRequest':
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # Make sure not to return `True` so that exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__
        await self.stop()

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize resources used by this class. Must be implemented by a subclass."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop & clear resources used by this class. Must be implemented by a subclass."""

    async def post(
        self,
        url: str,
        request_data: RequestData = None,
        timeout: float = None,
    ) -> Union[JSONDict, bool]:
        """Makes a request to the Bot API handles the return code and parses the answer.

        Warning:
            This method will be called by the methods of :class:`Bot` and should *not* be called
            manually.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            request_data (:class:`telegram.request.RequestData`, optional): An object describing
                any parameters and files to upload for the request.
            timeout (:obj:`float`, optional): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
          Dict[:obj:`str`, ...]: The JSON response of the Bot API.

        """
        result = await self._request_wrapper(
            method='POST', url=url, request_data=request_data, read_timeout=timeout
        )
        json_data = self._parse_json_response(result)
        # For successful requests, the results are in the 'result' entry
        # see https://core.telegram.org/bots/api#making-requests
        return json_data['result']

    async def retrieve(self, url: str, timeout: float = None) -> bytes:
        """Retrieve the contents of a file by its URL.

        Warning:
            This method will be called by the methods of :class:`Bot` and should *not* be called
            manually.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            timeout (:obj:`float`, optional): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
            :obj:`bytes`: The files contents.

        """
        return await self._request_wrapper(method='GET', url=url, read_timeout=timeout)

    async def _request_wrapper(
        self,
        method: str,
        url: str,
        request_data: RequestData = None,
        read_timeout: float = None,
    ) -> bytes:
        """Wraps the real implementation request method.

        Performs the following tasks:
        * Handle the various HTTP response codes.
        * Parse the Telegram server response.

        Args:
            method (:obj:`str`): HTTP method (i.e. 'POST', 'GET', etc.).
            url (:obj:`str`): The request's URL.
            request_data (:class:`telegram.request.RequestData`, optional): An object describing
                any parameters and files to upload for the request.
            read_timeout: Timeout for waiting to server's response.

        Returns:
            bytes: The payload part of the HTTP server response.

        Raises:
            TelegramError

        """
        # TGs response also has the fields 'ok' and 'error_code'.
        # However, we rather rely on the HTTP status code for now.

        try:
            code, payload = await self.do_request(
                method, url, request_data=request_data, read_timeout=read_timeout
            )
        except TelegramError as exc:
            raise exc
        except Exception as exc:
            raise NetworkError(f"Unknown error in HTTP implementation: {exc}") from exc

        if HTTPStatus.OK <= code <= 299:
            # 200-299 range are HTTP success statuses
            return payload

        try:
            response_data = self._parse_json_response(payload)

            # In some special cases, we ca raise more informative exceptions:
            # see https://core.telegram.org/bots/api#responseparameters and
            # https://core.telegram.org/bots/api#making-requests
            parameters = response_data.get('parameters')
            if parameters:
                migrate_to_chat_id = parameters.get('migrate_to_chat_id')
                if migrate_to_chat_id:
                    raise ChatMigrated(migrate_to_chat_id)
                retry_after = parameters.get('retry_after')
                if retry_after:
                    raise RetryAfter(retry_after)

            description = response_data.get('description')
            if description:
                message = description
            else:
                message = 'Unknown HTTPError'
        except ValueError:
            message = 'Unknown HTTPError'

        if code == HTTPStatus.FORBIDDEN:
            raise Forbidden(message)
        if code in (HTTPStatus.NOT_FOUND, HTTPStatus.UNAUTHORIZED):
            # TG returns 404 Not found for
            #   1) malformed tokens
            #   2) correct tokens but non-existing method, e.g. api.tg.org/botTOKEN/unkonwnMethod
            # We can basically rule out 2) since we don't let users make requests manually
            # TG returns 401 Unauthorized for correctly formatted tokens that are not valid
            raise InvalidToken(message)
        if code == HTTPStatus.BAD_REQUEST:
            raise BadRequest(message)
        if code == HTTPStatus.CONFLICT:
            raise Conflict(message)
        if code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
            raise NetworkError(
                'File too large to upload. Please check the limits at '
                'https://core.telegram.org/bots/api#senddocument'
            )
        if code == HTTPStatus.BAD_GATEWAY:
            raise NetworkError('Bad Gateway')
        raise NetworkError(f'{message} ({code})')

    @staticmethod
    def _parse_json_response(json_payload: bytes) -> JSONDict:
        """Try and parse the JSON returned from Telegram.

        Returns:
            dict: A JSON parsed as Python dict with results.

        Raises:
            TelegramError: If the data could not be json_loaded
        """
        decoded_s = json_payload.decode('utf-8', 'replace')
        try:
            return json.loads(decoded_s)
        except ValueError as exc:
            raise TelegramError('Invalid server response') from exc

    @staticmethod
    def json_dump(data: JSONDict) -> str:
        return json.dumps(data)

    @abc.abstractmethod
    async def do_request(
        self,
        method: str,
        url: str,
        request_data: RequestData = None,
        read_timeout: float = None,
        write_timeout: float = None,
    ) -> Tuple[int, bytes]:
        """Makes a request to the Bot API. Must be implemented by a subclass.

        Warning:
            This method will be called by :meth:`post` and :meth:`retrieve`. I should *not* be
            called manually.

        Args:
            method (:obj:`str`): HTTP method (i.e. ``'POST'``, ``'GET'``, etc.).
            url (:obj:`str`): The request's URL.
            request_data (:class:`telegram.request.RequestData`, optional): An object describing
                any parameters and files to upload for the request.
            read_timeout (:obj:`float`, optional): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).
            write_timeout (:obj:`float`, optional): If this value is specified, use it as the write
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
            Tuple[:obj:`int`, :obj:`bytes`]: The HTTP return code & the payload part of the server
            response.
        """
