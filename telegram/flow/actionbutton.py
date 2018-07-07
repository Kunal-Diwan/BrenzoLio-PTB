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
"""This module contains an object that represents a Telegram InlineKeyboardButton."""
from telegram import InlineKeyboardButton, KeyboardButton, TelegramObject
from telegram.flow.action import Action
from telegram.utils.binaryencoder import insert_callback_id


class ActionButton(TelegramObject):
    """This object represents one button of an inline keyboard.

    Note:
        You must use exactly one of the optional fields. Mind that :attr:`callback_game` is not
        working as expected. Putting a game short name in it might, but is not guaranteed to work.

    Attributes:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`): Optional. HTTP url to be opened when button is pressed.
        callback_data (:obj:`str`): Optional. Data to be sent in a callback query to the bot when
            button is pressed, 1-64 bytes.
        switch_inline_query (:obj:`str`): Optional. Will prompt the user to select one of their
            chats, open that chat and insert the bot's username and the specified inline query in
            the input field.
        switch_inline_query_current_chat (:obj:`str`): Optional. Will insert the bot's username and
            the specified inline query in the current chat's input field.
        callback_game (:class:`telegram.CallbackGame`): Optional. Description of the game that will
            be launched when the user presses the button.
        pay (:obj:`bool`): Optional. Specify True, to send a Pay button.

    Args:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`): HTTP url to be opened when button is pressed.
        callback_data (:obj:`str`, optional): Data to be sent in a callback query to the bot when
            button is pressed, 1-64 bytes.
        switch_inline_query (:obj:`str`, optional): If set, pressing the button will prompt the
            user to select one of their chats, open that chat and insert the bot's username and the
            specified inline query in the input field. Can be empty, in which case just the bot's
            username will be inserted. This offers an easy way for users to start using your bot
            in inline mode when they are currently in a private chat with it. Especially useful
            when combined with switch_pm* actions - in this case the user will be automatically
            returned to the chat they switched from, skipping the chat selection screen.
        switch_inline_query_current_chat (:obj:`str`, optional): If set, pressing the button will
            insert the bot's username and the specified inline query in the current chat's input
            field. Can be empty, in which case only the bot's username will be inserted. This
            offers a quick way for the user to open your bot in inline mode in the same chat - good
            for selecting something from multiple options.
        callback_game (:class:`telegram.CallbackGame`, optional): Description of the game that will
            be launched when the user presses the button. This type of button must always be
            the ``first`` button in the first row.
        pay (:obj:`bool`, optional): Specify True, to send a Pay button. This type of button must
            always be the ``first`` button in the first row.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 action,
                 caption=None,  # TODO DOCS: "will override..."
                 view_data=None,
                 switch_inline=None,
                 switch_inline_current_chat=None):

        if caption is None:
            if isinstance(action, Action):
                # noinspection PyProtectedMember
                if action._caption:
                    caption = action.get_caption(view_data)
                else:
                    raise ValueError("Neither this button nor its action have a caption. Pass the caption argument or "
                                     "set up your Action to have one.")
            else:
                raise ValueError("If the action is {} and not an Action object, a caption must be supplied as "
                                 "argument to this ActionButton.".format(type(action)))
        else:
            caption = action.get_caption(view_data)

        if len(caption) > 108:
            # We have a maximum button caption length of 128 characters until they are truncated
            # server-side. We will use the remaining 20 characters to encode a random ID.
            raise ValueError("Button caption must not be longer than 108 characters.")
        if caption in (None, ''):
            raise ValueError("Buttons without a text caption are not possible.")

        self.text = caption

        if switch_inline and switch_inline_current_chat:
            raise ValueError("Cannot set both switch_inline and switch_inline_current_chat.")
        self.switch_inline_query = switch_inline
        self.switch_inline_query_current_chat = switch_inline_current_chat

        self._action_id = action
        self._callback = None
        self.callback_data = None
        self._is_inline = None

        self._view_data = view_data

    def insert_callback(self, callback_manager):
        callback = callback_manager.create_callback(
            action_id=self._action_id,
            data=self._view_data,
            random_id=self._is_inline and not (self.switch_inline_query or self.switch_inline_query_current_chat)
        )

        self._callback = callback

        return callback

    @property
    def is_inline(self):
        return self._is_inline

    @is_inline.setter
    def is_inline(self, value):
        self._is_inline = value

    # noinspection PyAttributeOutsideInit
    def to_dict(self):
        if self._is_inline is None:
            raise ValueError("ActionButtons need to know whether they are inline or "
                             "regular keyboard buttons before usage.")
        if not self._callback:
            raise ValueError("You need to call the insert_callback method before usage.")

        if self.switch_inline_query or self.switch_inline_query_current_chat:
            if not self._is_inline:
                raise ValueError("switch_inline will not work with regular KeyboardButtons, "
                                 "use an InlineKeyboardMarkup instead.")

        if self._is_inline:
            self.__bases__ = (InlineKeyboardButton,)
        else:
            self.__bases__ = (KeyboardButton,)

        if not self._is_inline:
            # Regular KeyboardButton
            self.text = insert_callback_id(self.text, self._callback.id)
        elif self.switch_inline_query:
            # InlineKeyboardButton with switch_inline
            self.switch_inline_query = insert_callback_id(self.switch_inline_query, self._callback.id)
        elif self.switch_inline_query_current_chat:
            # InlineKeyboardButton with switch_inline_current_chat
            self.switch_inline_query_current_chat = insert_callback_id(self.switch_inline_query_current_chat,
                                                                       self._callback.id)
        else:
            # InlineKeyboardButton with callback_data
            self.callback_data = self._callback.id

        print(self.text, type(self), ': ',
              self.switch_inline_query or self.switch_inline_query_current_chat or self.callback_data)

        return super(ActionButton, self).to_dict()
