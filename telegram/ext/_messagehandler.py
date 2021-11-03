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
"""This module contains the MessageHandler class."""
from typing import TYPE_CHECKING, Callable, Dict, Optional, TypeVar, Union

from telegram import Update
from telegram.ext import filters as filters_module, Handler
from telegram._utils.defaultvalue import DefaultValue, DEFAULT_FALSE

from telegram.ext._utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class MessageHandler(Handler[Update, CCT]):
    """Handler class to handle telegram messages. They might contain text, media or status updates.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :mod:`telegram.ext.filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not). Default is
            :attr:`telegram.ext.filters.UPDATE`. This defaults to all message_type updates
            being: :attr:`Update.message`, :attr:`Update.edited_message`,
            :attr:`Update.channel_post` and :attr:`Update.edited_channel_post`.
            If you don't want or need any of those pass ``~filters.UpdateType.*`` in the filter
            argument.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Raises:
        ValueError

    Attributes:
        filters (:obj:`Filter`): Only allow updates with these Filters. See
            :mod:`telegram.ext.filters` for a full list of all available filters.
        callback (:obj:`callable`): The callback function for this handler.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('filters',)

    def __init__(
        self,
        filters: filters_module.BaseFilter,
        callback: Callable[[Update, CCT], RT],
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):

        super().__init__(callback, run_async=run_async)
        if filters is not None:
            self.filters = filters_module.UpdateType.ALL & filters
        else:
            self.filters = filters_module.UpdateType.ALL

    def check_update(self, update: object) -> Optional[Union[bool, Dict[str, list]]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update):
            return self.filters.check_update(update)
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: Optional[Union[bool, Dict[str, object]]],
    ) -> None:
        """Adds possible output of data filters to the :class:`CallbackContext`."""
        if isinstance(check_result, dict):
            context.update(check_result)
