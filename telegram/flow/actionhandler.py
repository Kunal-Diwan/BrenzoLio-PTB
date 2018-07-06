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
from telegram.flow.action import Action
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.handler import Handler
from telegram.flow.inlineactionhandler import InlineActionHandler
from telegram.flow.replyactionhandler import ReplyActionHandler


class ActionHandler(Handler):
    def __init__(self,
                 action,
                 callback,
                 filters=None,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(ActionHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

        self.action = action
        self.filters = filters

        self.sub_handlers = []

        # Button handlers are always possible just by providing an ID
        if action.buttons:
            self.sub_handlers.append(ReplyActionHandler(action.id, callback))
        if action.inline_buttons:
            self.sub_handlers.append(InlineActionHandler(action.id, callback))

        if isinstance(action, Action):
            # Advanced handlers only work with dedicated `Action` objects
            if action.commands:
                self.sub_handlers.append(
                    CommandHandler(action.commands, callback)
                )

    def check_update(self, update, dispatcher):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

            Args:
            update (:class:`telegram.Update`): Incoming telegram update.

            Returns:
            :obj:`bool`

            """
        for handler in self.sub_handlers:
            res = handler.check_update(update, dispatcher)
            if res is not None and res is not False:
                return res, handler

    def collect_additional_context(self, context, update, dispatcher, check_result):
        check_result, handler = check_result

        handler.collect_additional_context(context, update, dispatcher, check_result)
