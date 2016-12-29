#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents ProxyTests for Telegram Message"""

from datetime import datetime
import os
import sys
import unittest

sys.path.append('.')

from flaky import flaky
from telegram.utils.request import Request
import telegram

from tests.base import BaseTest, timeout


class AnonymousHttpsProxyTest(BaseTest, unittest.TestCase):
    """This object represents AnonymousHttpsProxyTest for Telegram MessageTest."""

    @classmethod
    def setUpClass(cls):
        # Proxy taken from https://sslproxies.org .
        cls._bot = telegram.Bot(
            os.environ.get('TOKEN', '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0'),
            request=Request(proxy_url='https://91.195.183.57:3128'))

    @flaky(3, 1)
    @timeout(10)
    def testSendMessage(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id, text='Моё судно на воздушной подушке полно угрей')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(10)
    def test_reply_text(self):
        """Test for a proxied Message.reply_text"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_text('Testing proxy mode.')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Testing proxy mode.')


class AnonymousHttpProxyTest(BaseTest, unittest.TestCase):
    """This object represents AnonymousHttpProxyTest for Telegram MessageTest."""

    @classmethod
    def setUpClass(cls):
        # Proxy taken from https://incloak.com .
        cls._bot = telegram.Bot(
            os.environ.get('TOKEN', '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0'),
            request=Request(proxy_url='http://138.201.63.123:31288'))

    @timeout(15)
    @flaky(3, 1)
    def testSendMessage(self):
        message = self._bot.sendMessage(
            chat_id=self._chat_id, text='Моё судно на воздушной подушке полно угрей')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, u'Моё судно на воздушной подушке полно угрей')
        self.assertTrue(isinstance(message.date, datetime))

    @flaky(3, 1)
    @timeout(15)
    def test_reply_text(self):
        """Test for a proxied Message.reply_text"""
        message = self._bot.sendMessage(self._chat_id, '.')
        message = message.reply_text('Testing proxy mode.')

        self.assertTrue(self.is_json(message.to_json()))
        self.assertEqual(message.text, 'Testing proxy mode.')


if __name__ == '__main__':
    unittest.main()
