#!/usr/bin/env python
#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2021
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an class that holds a parameters of a request to the Bot API."""
from dataclasses import dataclass
from typing import List, Dict, Any, Union
from urllib.parse import urlencode

from telegram._utils.types import UploadFileDict
from telegram.request._requestparameter import RequestParameter

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]  # noqa: F723


@dataclass
class RequestData:
    """Instances of this class represent a collection of parameters and files to be sent along
    with a request to the Bot API.

    .. versionadded:: 14.0

    Warning:
        How exactly instances of this will are created should be considered an implementation
        detail and not part of PTBs public API. Users should exclusively rely on the documented
        attributes, properties and methods.

    Attributes:
        contains_files (:obj:`bool`): Whether this object contains files to be uploaded via
            ``multipart/form-data``.
    """

    __slots__ = ('_parameters', 'contains_files')

    def __init__(
        self,
        parameters: List[RequestParameter] = None,
    ):
        self._parameters = parameters or []
        self.contains_files = any(param.input_files for param in self._parameters)

    @property
    def parameters(self) -> Dict[str, Union[str, int, List, Dict]]:
        """Gives the parameters as mapping of parameter name to the parameter value, which can be
        a single object of type :obj:`int`, :obj:`float`, :obj:`str` or :obj:`bool` or any
        (possibly nested) composition of lists, tuples and dictionaries, where each entry, key
        and value is of one of the mentioned types.
        """
        return {param.name: param.value for param in self._parameters}  # type: ignore[misc]

    @property
    def json_parameters(self) -> Dict[str, str]:
        """Gives the parameters as mapping of parameter name to the respective JSON encoded
        value.
        """
        return {param.name: param.json_value for param in self._parameters}

    def url_encoded_parameters(self, encode_kwargs: Dict[str, Any] = None) -> str:
        """Encodes the parameters with :meth:`urllib.parse.urlencode`.

        Args:
            encode_kwargs (Dict[:obj:`str`, any], optional): Additional keyword arguments to pass
                along to :meth:`urllib.parse.urlencode`.
        """
        if encode_kwargs:
            return urlencode(self.json_parameters, **encode_kwargs)
        return urlencode(self.json_parameters)

    def build_parametrized_url(self, url: str, encode_kwargs: Dict[str, Any] = None) -> str:
        """Shortcut for attaching the return value of :meth:`url_encoded_parameters` to the
        :attr:`url`.

        Args:
            encode_kwargs (Dict[:obj:`str`, any], optional): Additional keyword arguments to pass
                along to :meth:`urllib.parse.urlencode`.
        """
        url_parameters = self.url_encoded_parameters(encode_kwargs=encode_kwargs)
        return f'{url}?{url_parameters}'

    @property
    def json_payload(self) -> bytes:
        """The parameters as UTF-8 encoded JSON payload."""
        return json.dumps(self.json_parameters).encode('utf-8')

    @property
    def multipart_data(self) -> UploadFileDict:
        """Gives the files contained in this object as mapping of part name to encoded content."""
        multipart_data: UploadFileDict = {}
        for param in self._parameters:
            m_data = param.multipart_data
            if m_data:
                multipart_data.update(m_data)
        return multipart_data
