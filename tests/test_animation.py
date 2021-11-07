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
import os
from pathlib import Path

import pytest
from flaky import flaky

from telegram import PhotoSize, Animation, Voice, MessageEntity, Bot
from telegram.error import BadRequest, TelegramError
from telegram.helpers import escape_markdown
from telegram.request import RequestData
from tests.conftest import (
    check_shortcut_call,
    check_shortcut_signature,
    check_defaults_handling,
    data_file,
)


@pytest.fixture(scope='function')
def animation_file():
    f = data_file('game.gif').open('rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
@pytest.mark.asyncio
async def animation(bot, chat_id):
    with data_file('game.gif').open('rb') as f:
        thumb = data_file('thumb.jpg')
        return (
            await bot.send_animation(chat_id, animation=f, timeout=50, thumb=thumb.open('rb'))
        ).animation


class TestAnimation:
    animation_file_id = 'CgADAQADngIAAuyVeEez0xRovKi9VAI'
    animation_file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'
    width = 320
    height = 180
    duration = 1
    # animation_file_url = 'https://python-telegram-bot.org/static/testfiles/game.gif'
    # Shortened link, the above one is cached with the wrong duration.
    animation_file_url = 'http://bit.ly/2L18jua'
    file_name = 'game.gif.mp4'
    mime_type = 'video/mp4'
    file_size = 4127
    caption = "Test *animation*"

    def test_slot_behaviour(self, animation, mro_slots):
        for attr in animation.__slots__:
            assert getattr(animation, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(animation)) == len(set(mro_slots(animation))), "duplicate slot"

    def test_creation(self, animation):
        assert isinstance(animation, Animation)
        assert isinstance(animation.file_id, str)
        assert isinstance(animation.file_unique_id, str)
        assert animation.file_id != ''
        assert animation.file_unique_id != ''

    def test_expected_values(self, animation):
        assert animation.file_size == self.file_size
        assert animation.mime_type == self.mime_type
        assert animation.file_name == self.file_name
        assert isinstance(animation.thumb, PhotoSize)

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_all_args(self, bot, chat_id, animation_file, animation, thumb_file):
        message = await bot.send_animation(
            chat_id,
            animation_file,
            duration=self.duration,
            width=self.width,
            height=self.height,
            caption=self.caption,
            parse_mode='Markdown',
            disable_notification=False,
            thumb=thumb_file,
        )

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert isinstance(message.animation.file_unique_id, str)
        assert message.animation.file_id != ''
        assert message.animation.file_unique_id != ''
        assert message.animation.file_name == animation.file_name
        assert message.animation.mime_type == animation.mime_type
        assert message.animation.file_size == animation.file_size
        assert message.animation.thumb.width == self.width
        assert message.animation.thumb.height == self.height

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_animation_custom_filename(self, bot, chat_id, animation_file, monkeypatch):
        async def make_assertion(url, request_data: RequestData, read_timeout):
            return list(request_data.multipart_data.values())[0][0] == 'custom_filename'

        monkeypatch.setattr(bot.request, 'post', make_assertion)

        assert await bot.send_animation(chat_id, animation_file, filename='custom_filename')
        monkeypatch.delattr(bot.request, 'post')

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_get_and_download(self, bot, animation):
        path = Path('game.gif')
        if path.is_file():
            path.unlink()

        new_file = await bot.get_file(animation.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == animation.file_id
        assert new_file.file_path.startswith('https://')

        new_filepath = await new_file.download('game.gif')

        assert new_filepath.is_file()

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_animation_url_file(self, bot, chat_id, animation):
        message = await bot.send_animation(
            chat_id=chat_id, animation=self.animation_file_url, caption=self.caption
        )

        assert message.caption == self.caption

        assert isinstance(message.animation, Animation)
        assert isinstance(message.animation.file_id, str)
        assert isinstance(message.animation.file_unique_id, str)
        assert message.animation.file_id != ''
        assert message.animation.file_unique_id != ''

        assert message.animation.duration == animation.duration
        assert message.animation.file_name == animation.file_name
        assert message.animation.mime_type == animation.mime_type
        assert message.animation.file_size == animation.file_size

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_animation_caption_entities(self, bot, chat_id, animation):
        test_string = 'Italic Bold Code'
        entities = [
            MessageEntity(MessageEntity.ITALIC, 0, 6),
            MessageEntity(MessageEntity.ITALIC, 7, 4),
            MessageEntity(MessageEntity.ITALIC, 12, 4),
        ]
        message = await bot.send_animation(
            chat_id, animation, caption=test_string, caption_entities=entities
        )

        assert message.caption == test_string
        assert message.caption_entities == entities

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_animation_default_parse_mode_1(self, default_bot, chat_id, animation_file):
        test_string = 'Italic Bold Code'
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string
        )
        assert message.caption_markdown == test_markdown_string
        assert message.caption == test_string

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_animation_default_parse_mode_2(self, default_bot, chat_id, animation_file):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string, parse_mode=None
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @flaky(3, 1)
    @pytest.mark.parametrize('default_bot', [{'parse_mode': 'Markdown'}], indirect=True)
    @pytest.mark.asyncio
    async def test_send_animation_default_parse_mode_3(self, default_bot, chat_id, animation_file):
        test_markdown_string = '_Italic_ *Bold* `Code`'

        message = await default_bot.send_animation(
            chat_id, animation_file, caption=test_markdown_string, parse_mode='HTML'
        )
        assert message.caption == test_markdown_string
        assert message.caption_markdown == escape_markdown(test_markdown_string)

    @pytest.mark.asyncio
    async def test_send_animation_local_files(self, monkeypatch, bot, chat_id):
        # For just test that the correct paths are passed as we have no local bot API set up
        test_flag = False
        file = data_file('telegram.jpg')
        expected = file.as_uri()

        async def make_assertion(_, data, *args, **kwargs):
            nonlocal test_flag
            test_flag = data.get('animation') == expected and data.get('thumb') == expected

        monkeypatch.setattr(bot, '_post', make_assertion)
        await bot.send_animation(chat_id, file, thumb=file)
        assert test_flag
        monkeypatch.delattr(bot, '_post')

    @flaky(3, 1)
    @pytest.mark.parametrize(
        'default_bot,custom',
        [
            ({'allow_sending_without_reply': True}, None),
            ({'allow_sending_without_reply': False}, None),
            ({'allow_sending_without_reply': False}, True),
        ],
        indirect=['default_bot'],
    )
    @pytest.mark.asyncio
    async def test_send_animation_default_allow_sending_without_reply(
        self, default_bot, chat_id, animation, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, 'test')
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_animation(
                chat_id,
                animation,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_animation(
                chat_id, animation, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                await default_bot.send_animation(
                    chat_id, animation, reply_to_message_id=reply_to_message.message_id
                )

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_resend(self, bot, chat_id, animation):
        message = await bot.send_animation(chat_id, animation.file_id)

        assert message.animation == animation

    @pytest.mark.asyncio
    async def test_send_with_animation(self, monkeypatch, bot, chat_id, animation):
        async def make_assertion(url, request_data: RequestData, read_timeout):
            return request_data.json_parameters['animation'] == animation.file_id

        monkeypatch.setattr(bot.request, 'post', make_assertion)
        message = await bot.send_animation(animation=animation, chat_id=chat_id)
        assert message

    def test_de_json(self, bot, animation):
        json_dict = {
            'file_id': self.animation_file_id,
            'file_unique_id': self.animation_file_unique_id,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumb': animation.thumb.to_dict(),
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
        }
        animation = Animation.de_json(json_dict, bot)
        assert animation.file_id == self.animation_file_id
        assert animation.file_unique_id == self.animation_file_unique_id
        assert animation.file_name == self.file_name
        assert animation.mime_type == self.mime_type
        assert animation.file_size == self.file_size

    def test_to_dict(self, animation):
        animation_dict = animation.to_dict()

        assert isinstance(animation_dict, dict)
        assert animation_dict['file_id'] == animation.file_id
        assert animation_dict['file_unique_id'] == animation.file_unique_id
        assert animation_dict['width'] == animation.width
        assert animation_dict['height'] == animation.height
        assert animation_dict['duration'] == animation.duration
        assert animation_dict['thumb'] == animation.thumb.to_dict()
        assert animation_dict['file_name'] == animation.file_name
        assert animation_dict['mime_type'] == animation.mime_type
        assert animation_dict['file_size'] == animation.file_size

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file(self, bot, chat_id):
        animation_file = open(os.devnull, 'rb')

        with pytest.raises(TelegramError):
            await bot.send_animation(chat_id=chat_id, animation=animation_file)

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_animation(chat_id=chat_id, animation='')

    @pytest.mark.asyncio
    async def test_error_send_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_animation(chat_id=chat_id)

    @pytest.mark.asyncio
    async def test_get_file_instance_method(self, monkeypatch, animation):
        async def make_assertion(*_, **kwargs):
            return kwargs['file_id'] == animation.file_id

        assert check_shortcut_signature(Animation.get_file, Bot.get_file, ['file_id'], [])
        assert await check_shortcut_call(animation.get_file, animation.get_bot(), 'get_file')
        assert await check_defaults_handling(animation.get_file, animation.get_bot())

        monkeypatch.setattr(animation.get_bot(), 'get_file', make_assertion)
        assert await animation.get_file()

    def test_equality(self):
        a = Animation(
            self.animation_file_id,
            self.animation_file_unique_id,
            self.height,
            self.width,
            self.duration,
        )
        b = Animation('', self.animation_file_unique_id, self.height, self.width, self.duration)
        d = Animation('', '', 0, 0, 0)
        e = Voice(self.animation_file_id, self.animation_file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
