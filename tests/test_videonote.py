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

from telegram import VideoNote, Voice, PhotoSize, Bot
from telegram.error import BadRequest, TelegramError
from telegram.request import RequestData
from tests.conftest import (
    check_shortcut_call,
    check_shortcut_signature,
    check_defaults_handling,
    data_file,
)


@pytest.fixture(scope='function')
def video_note_file():
    f = data_file('telegram2.mp4').open('rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
@pytest.mark.asyncio
async def video_note(bot, chat_id):
    with data_file('telegram2.mp4').open('rb') as f:
        return (await bot.send_video_note(chat_id, video_note=f, timeout=50)).video_note


class TestVideoNote:
    length = 240
    duration = 3
    file_size = 132084

    thumb_width = 240
    thumb_height = 240
    thumb_file_size = 11547

    caption = 'VideoNoteTest - Caption'
    videonote_file_id = '5a3128a4d2a04750b5b58397f3b5e812'
    videonote_file_unique_id = 'adc3145fd2e84d95b64d68eaa22aa33e'

    def test_creation(self, video_note):
        # Make sure file has been uploaded.
        assert isinstance(video_note, VideoNote)
        assert isinstance(video_note.file_id, str)
        assert isinstance(video_note.file_unique_id, str)
        assert video_note.file_id != ''
        assert video_note.file_unique_id != ''

        assert isinstance(video_note.thumb, PhotoSize)
        assert isinstance(video_note.thumb.file_id, str)
        assert isinstance(video_note.thumb.file_unique_id, str)
        assert video_note.thumb.file_id != ''
        assert video_note.thumb.file_unique_id != ''

    def test_expected_values(self, video_note):
        assert video_note.length == self.length
        assert video_note.duration == self.duration
        assert video_note.file_size == self.file_size

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_all_args(self, bot, chat_id, video_note_file, video_note, thumb_file):
        message = await bot.send_video_note(
            chat_id,
            video_note_file,
            duration=self.duration,
            length=self.length,
            disable_notification=False,
            thumb=thumb_file,
        )

        assert isinstance(message.video_note, VideoNote)
        assert isinstance(message.video_note.file_id, str)
        assert isinstance(message.video_note.file_unique_id, str)
        assert message.video_note.file_id != ''
        assert message.video_note.file_unique_id != ''
        assert message.video_note.length == video_note.length
        assert message.video_note.duration == video_note.duration
        assert message.video_note.file_size == video_note.file_size

        assert message.video_note.thumb.file_size == self.thumb_file_size
        assert message.video_note.thumb.width == self.thumb_width
        assert message.video_note.thumb.height == self.thumb_height

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_send_video_note_custom_filename(
        self, bot, chat_id, video_note_file, monkeypatch
    ):
        async def make_assertion(url, request_data: RequestData, read_timeout):
            return list(request_data.multipart_data.values())[0][0] == 'custom_filename'

        monkeypatch.setattr(bot.request, 'post', make_assertion)

        assert await bot.send_video_note(chat_id, video_note_file, filename='custom_filename')

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_get_and_download(self, bot, video_note):
        path = Path('telegram2.mp4')
        if path.is_file():
            path.unlink()

        new_file = await bot.get_file(video_note.file_id)

        assert new_file.file_size == self.file_size
        assert new_file.file_id == video_note.file_id
        assert new_file.file_unique_id == video_note.file_unique_id
        assert new_file.file_path.startswith('https://')

        await new_file.download('telegram2.mp4')

        assert path.is_file()

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_resend(self, bot, chat_id, video_note):
        message = await bot.send_video_note(chat_id, video_note.file_id)

        assert message.video_note == video_note

    @pytest.mark.asyncio
    async def test_send_with_video_note(self, monkeypatch, bot, chat_id, video_note):
        async def make_assertion(url, request_data: RequestData, read_timeout):
            return request_data.json_parameters['video_note'] == video_note.file_id

        monkeypatch.setattr(bot.request, 'post', make_assertion)
        message = await bot.send_video_note(chat_id, video_note=video_note)
        assert message

    def test_de_json(self, bot):
        json_dict = {
            'file_id': self.videonote_file_id,
            'file_unique_id': self.videonote_file_unique_id,
            'length': self.length,
            'duration': self.duration,
            'file_size': self.file_size,
        }
        json_video_note = VideoNote.de_json(json_dict, bot)

        assert json_video_note.file_id == self.videonote_file_id
        assert json_video_note.file_unique_id == self.videonote_file_unique_id
        assert json_video_note.length == self.length
        assert json_video_note.duration == self.duration
        assert json_video_note.file_size == self.file_size

    def test_to_dict(self, video_note):
        video_note_dict = video_note.to_dict()

        assert isinstance(video_note_dict, dict)
        assert video_note_dict['file_id'] == video_note.file_id
        assert video_note_dict['file_unique_id'] == video_note.file_unique_id
        assert video_note_dict['length'] == video_note.length
        assert video_note_dict['duration'] == video_note.duration
        assert video_note_dict['file_size'] == video_note.file_size

    @pytest.mark.asyncio
    async def test_send_video_note_local_files(self, monkeypatch, bot, chat_id):
        # For just test that the correct paths are passed as we have no local bot API set up
        test_flag = False
        file = data_file('telegram.jpg')
        expected = file.as_uri()

        async def make_assertion(_, data, *args, **kwargs):
            nonlocal test_flag
            test_flag = data.get('video_note') == expected and data.get('thumb') == expected

        monkeypatch.setattr(bot, '_post', make_assertion)
        await bot.send_video_note(chat_id, file, thumb=file)
        assert test_flag

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
    async def test_send_video_note_default_allow_sending_without_reply(
        self, default_bot, chat_id, video_note, custom
    ):
        reply_to_message = await default_bot.send_message(chat_id, 'test')
        await reply_to_message.delete()
        if custom is not None:
            message = await default_bot.send_video_note(
                chat_id,
                video_note,
                allow_sending_without_reply=custom,
                reply_to_message_id=reply_to_message.message_id,
            )
            assert message.reply_to_message is None
        elif default_bot.defaults.allow_sending_without_reply:
            message = await default_bot.send_video_note(
                chat_id, video_note, reply_to_message_id=reply_to_message.message_id
            )
            assert message.reply_to_message is None
        else:
            with pytest.raises(BadRequest, match='message not found'):
                await default_bot.send_video_note(
                    chat_id, video_note, reply_to_message_id=reply_to_message.message_id
                )

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_video_note(chat_id, open(os.devnull, 'rb'))

    @flaky(3, 1)
    @pytest.mark.asyncio
    async def test_error_send_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            await bot.send_video_note(chat_id, '')

    @pytest.mark.asyncio
    async def test_error_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            await bot.send_video_note(chat_id=chat_id)

    @pytest.mark.asyncio
    async def test_get_file_instance_method(self, monkeypatch, video_note):
        async def make_assertion(*_, **kwargs):
            return kwargs['file_id'] == video_note.file_id

        assert check_shortcut_signature(VideoNote.get_file, Bot.get_file, ['file_id'], [])
        assert await check_shortcut_call(video_note.get_file, video_note.get_bot(), 'get_file')
        assert await check_defaults_handling(video_note.get_file, video_note.get_bot())

        monkeypatch.setattr(video_note.get_bot(), 'get_file', make_assertion)
        assert await video_note.get_file()

    def test_equality(self, video_note):
        a = VideoNote(video_note.file_id, video_note.file_unique_id, self.length, self.duration)
        b = VideoNote('', video_note.file_unique_id, self.length, self.duration)
        c = VideoNote(video_note.file_id, video_note.file_unique_id, 0, 0)
        d = VideoNote('', '', self.length, self.duration)
        e = Voice(video_note.file_id, video_note.file_unique_id, self.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
