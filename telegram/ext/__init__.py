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
"""Extensions over the Telegram Bot API to facilitate bot making"""
from telegram.flow.action import Action, ActionRepository, RerouteToAction, ViewModel
from telegram.flow.actionhandler import ActionHandler
from telegram.flow.actionbutton import ActionButton
from telegram.flow.inlineactionhandler import InlineActionHandler
from telegram.flow.replyactionhandler import ReplyActionHandler
from .callbackcontext import CallbackContext
from .callbackqueryhandler import CallbackQueryHandler
from .choseninlineresulthandler import ChosenInlineResultHandler
from .commandhandler import CommandHandler, PrefixHandler
from .conversationhandler import ConversationHandler
from .dispatcher import Dispatcher, DispatcherHandlerStop, run_async
from .filters import BaseFilter, Filters
from .handler import Handler
from .inlinequeryhandler import InlineQueryHandler
from .jobqueue import Job, JobQueue
from .messagehandler import MessageHandler
from .messagequeue import DelayQueue, MessageQueue
from .precheckoutqueryhandler import PreCheckoutQueryHandler
from .regexhandler import RegexHandler
from .shippingqueryhandler import ShippingQueryHandler
from .stringcommandhandler import StringCommandHandler
from .stringregexhandler import StringRegexHandler
from .typehandler import TypeHandler
from .updater import Updater

SPECIAL_PTB_DISPATCHER_GROUP = -12345

__all__ = ('Dispatcher', 'JobQueue', 'Job', 'Updater', 'CallbackQueryHandler',
           'ChosenInlineResultHandler', 'CommandHandler', 'Handler', 'InlineQueryHandler',
           'MessageHandler', 'BaseFilter', 'Filters', 'RegexHandler', 'StringCommandHandler',
           'StringRegexHandler', 'TypeHandler', 'ConversationHandler',
           'PreCheckoutQueryHandler', 'ShippingQueryHandler', 'MessageQueue', 'DelayQueue',
           'DispatcherHandlerStop', 'run_async', 'CallbackContext', 'PrefixHandler', 'Action',
           'ActionHandler', 'InlineActionHandler', 'ReplyActionHandler', 'ActionButton',
           'ActionRepository', 'RerouteToAction', 'ViewModel')
