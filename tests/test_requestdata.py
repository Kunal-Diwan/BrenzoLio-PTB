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
import datetime
import json
from typing import Any, Dict

import pytest

from telegram import InputFile, MessageEntity, InputMediaPhoto, InputMediaVideo
from telegram.constants import ChatType
from telegram.request import RequestData
from telegram.request._requestparameter import RequestParameter
from tests.conftest import data_file


@pytest.fixture(scope='module')
def inputfile() -> InputFile:
    return InputFile(data_file('telegram.jpg').read_bytes())


@pytest.fixture(scope='module')
def input_media_video() -> InputMediaVideo:
    return InputMediaVideo(
        media=data_file('telegram.mp4').read_bytes(),
        thumb=data_file('telegram.jpg').read_bytes(),
    )


@pytest.fixture(scope='module')
def input_media_photo() -> InputMediaPhoto:
    return InputMediaPhoto(media=data_file('telegram.jpg').read_bytes())


@pytest.fixture(scope='module')
def simple_params() -> Dict[str, Any]:
    return {
        'string': 'string',
        'integer': 1,
        'tg_object': MessageEntity('type', 1, 1).to_dict(),
        'list': [1, 'string', MessageEntity('type', 1, 1).to_dict()],
    }


@pytest.fixture(scope='module')
def simple_jsons() -> Dict[str, Any]:
    return {
        'string': 'string',
        'integer': json.dumps(1),
        'tg_object': MessageEntity('type', 1, 1).to_json(),
        'list': json.dumps([1, 'string', MessageEntity('type', 1, 1).to_dict()]),
    }


@pytest.fixture(scope='module')
def simple_rqs(simple_params) -> RequestData:
    return RequestData(
        [RequestParameter.from_input(key, value) for key, value in simple_params.items()]
    )


@pytest.fixture(scope='module')
def file_params(inputfile, input_media_video, input_media_photo) -> Dict[str, Any]:
    return {
        'inputfile': inputfile,
        'inputmedia': input_media_video,
        'inputmedia_list': [input_media_video, input_media_photo],
    }


@pytest.fixture(scope='module')
def file_jsons(inputfile, input_media_video, input_media_photo) -> Dict[str, Any]:
    input_media_video_dict = input_media_video.to_dict()
    input_media_video_dict['media'] = input_media_video.media.attach_uri
    input_media_video_dict['thumb'] = input_media_video.thumb.attach_uri
    input_media_photo_dict = input_media_photo.to_dict()
    input_media_photo_dict['media'] = input_media_photo.media.attach_uri
    return {
        'inputfile': inputfile.attach_uri,
        'inputmedia': json.dumps(input_media_video_dict),
        'inputmedia_list': json.dumps([input_media_video_dict, input_media_photo_dict]),
    }


@pytest.fixture(scope='module')
def file_rqs(file_params) -> RequestData:
    return RequestData(
        [RequestParameter.from_input(key, value) for key, value in file_params.items()]
    )


@pytest.fixture()
def mixed_params(file_params, simple_params) -> Dict[str, Any]:
    both = file_params.copy()
    both.update(simple_params)
    return both


@pytest.fixture()
def mixed_jsons(file_jsons, simple_jsons) -> Dict[str, Any]:
    both = file_jsons.copy()
    both.update(simple_jsons)
    return both


@pytest.fixture()
def mixed_rqs(mixed_params) -> RequestData:
    return RequestData(
        [RequestParameter.from_input(key, value) for key, value in mixed_params.items()]
    )


class TestRequestData:
    def test_contains_files(self, simple_rqs, file_rqs, mixed_rqs):
        assert not simple_rqs.contains_files
        assert file_rqs.contains_files
        assert mixed_rqs.contains_files

    def test_parameters(
        self, simple_rqs, file_rqs, mixed_rqs, simple_params, file_params, mixed_params
    ):
        assert simple_rqs.parameters == simple_params
        assert file_rqs.parameters == file_params
        assert mixed_rqs.parameters == mixed_params

    def test_json_parameters(
        self, simple_rqs, file_rqs, mixed_rqs, simple_jsons, file_jsons, mixed_jsons
    ):
        assert simple_rqs.parameters == simple_jsons
        assert file_rqs.parameters == file_jsons
        assert mixed_rqs.parameters == mixed_jsons

    # @pytest.mark.parametrize(
    #     'value, expected',
    #     [
    #         (1, '1'),
    #         ('one', 'one'),
    #         (True, 'true'),
    #         (None, 'null'),
    #         ([1, '1'], '[1, "1"]'),
    #         ({True: None}, '{"true": null}'),
    #         ((1,), '[1]'),
    #     ],
    # )
    # def test_json_value(self, value, expected):
    #     request_parameter = RequestParameter('name', value, None)
    #     assert request_parameter.json_value == expected
    #
    # def test_multipart_data(self):
    #     assert RequestParameter('name', 'value', []).multipart_data is None
    #
    #     input_file_1 = InputFile(data_file('telegram.jpg').read_bytes())
    #     input_file_2 = InputFile(data_file('telegram.jpg').read_bytes(), filename='custom')
    #     request_parameter = RequestParameter('value', 'name', [input_file_1, input_file_2])
    #     files = request_parameter.multipart_data
    #     assert files[input_file_1.attach_name] == input_file_1.field_tuple
    #     assert files[input_file_2.attach_name] == input_file_2.field_tuple
    #
    # @pytest.mark.parametrize(
    #     ('value', 'expected_value'),
    #     [
    #         (True, True),
    #         ('str', 'str'),
    #         ({1: 1.0}, {1: 1.0}),
    #         (ChatType.PRIVATE, 'private'),
    #         (MessageEntity('type', 1, 1), {'type': 'type', 'offset': 1, 'length': 1}),
    #         (datetime.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5), 1573431976),
    #         (
    #             [
    #                 True,
    #                 'str',
    #                 MessageEntity('type', 1, 1),
    #                 ChatType.PRIVATE,
    #                 datetime.datetime(2019, 11, 11, 0, 26, 16, 10 ** 5),
    #             ],
    #             [True, 'str', {'type': 'type', 'offset': 1, 'length': 1}, 'private', 1573431976],
    #         ),
    #     ],
    # )
    # def test_from_input_no_media(self, value, expected_value):
    #     request_parameter = RequestParameter.from_input('key', value)
    #     assert request_parameter.value == expected_value
    #     assert request_parameter.input_files is None
    #
    # def test_from_input_inputfile(self):
    #     inputfile_1 = InputFile(data_file('telegram.jpg').read_bytes(), 'inputfile_1')
    #     inputfile_2 = InputFile(data_file('telegram.mp4').read_bytes(), 'inputfile_2')
    #
    #     request_parameter = RequestParameter.from_input('key', inputfile_1)
    #     assert request_parameter.value == inputfile_1.attach_uri
    #     assert request_parameter.input_files == [inputfile_1]
    #
    #     request_parameter = RequestParameter.from_input('key', [inputfile_1, inputfile_2])
    #     assert request_parameter.value == [inputfile_1.attach_uri, inputfile_2.attach_uri]
    #     assert request_parameter.input_files == [inputfile_1, inputfile_2]
    #
    # def test_from_input_input_media(self):
    #     input_media_no_thumb = InputMediaPhoto(media=data_file('telegram.jpg').read_bytes())
    #     input_media_thumb = InputMediaVideo(
    #         media=data_file('telegram.mp4').read_bytes(),
    #         thumb=data_file('telegram.jpg').read_bytes(),
    #     )
    #
    #     request_parameter = RequestParameter.from_input('key', input_media_no_thumb)
    #     expected_no_thumb = input_media_no_thumb.to_dict()
    #     expected_no_thumb.update({'media': input_media_no_thumb.media.attach_uri})
    #     assert request_parameter.value == expected_no_thumb
    #     assert request_parameter.input_files == [input_media_no_thumb.media]
    #
    #     request_parameter = RequestParameter.from_input('key', input_media_thumb)
    #     expected_thumb = input_media_thumb.to_dict()
    #     expected_thumb.update({'media': input_media_thumb.media.attach_uri})
    #     expected_thumb.update({'thumb': input_media_thumb.thumb.attach_uri})
    #     assert request_parameter.value == expected_thumb
    #     assert request_parameter.input_files == [input_media_thumb.media, input_media_thumb.thumb]
    #
    #     request_parameter = RequestParameter.from_input(
    #         'key', [input_media_thumb, input_media_no_thumb]
    #     )
    #     assert request_parameter.value == [expected_thumb, expected_no_thumb]
    #     assert request_parameter.input_files == [
    #         input_media_thumb.media,
    #         input_media_thumb.thumb,
    #         input_media_no_thumb.media,
    #     ]
