#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
"""This module contains the ChosenInlineResultHandler class."""
import collections

from telegram import Update
from telegram.ext import Handler
from telegram.flow.action import get_action_id


class ChosenInlineActionHandler(Handler):
    """Handler class to handle Telegram updates that contain a chosen inline result.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Optional. Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Optional. Determines whether ``chat_data`` will be passed to
            the callback function.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

        Note that this is DEPRECATED, and you should use context based callbacks. See
        https://git.io/vp113 for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.

    """

    def __init__(self, action, callback, pass_update_queue=False, pass_job_queue=False, pass_user_data=False,
                 pass_chat_data=False):
        super().__init__(callback, pass_update_queue, pass_job_queue, pass_user_data, pass_chat_data)
        self.action_id = get_action_id(action)

        # Hold back three of the most recent updates so a message can be inserted in the ChosenInlineResult
        self.__most_recent_updates = collections.deque(maxlen=3)

    def check_update(self, update, dispatcher):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update):
            if update.chosen_inline_result:
                action_id = dispatcher.callback_manager.peek_action(
                    update.chosen_inline_result.result_id
                )
                return action_id == self.action_id
            elif update.message:
                self.__most_recent_updates.appendleft(update)

    def collect_additional_context(self, context, update, dispatcher, check_result):
        callback_item = dispatcher.callback_manager.lookup_callback(
            update.chosen_inline_result.result_id
        )

        # Insert the held-back Message object into this ChosenInlineResult when applicable
        for ud in self.__most_recent_updates:
            if ud.effective_user.id == update.effective_user.id:
                update.message = ud.message

        context.view_model = callback_item.model_data
