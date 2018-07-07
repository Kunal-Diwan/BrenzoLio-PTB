from abc import ABCMeta, abstractmethod
from uuid import uuid4

from telegram.flow.action import get_action_id
from telegram.utils.binaryencoder import callback_id_from_query, _obfuscate_id_binary


class CallbackNotFound(Exception):
    pass

    # TODO: Load initial (current) counter value from persistence on startup


# class Serializer(object):
#     raise NotImplemented  # TODO

class CallbackItem(object):
    def __init__(self, id, action, data, one_time_callback=False):
        self.id = id
        self.action_id = get_action_id(action)

        if hasattr(action, 'model_type'):
            self.model_type = action.model_type

        self.model_data = data
        self.chat_id = None
        self.one_time_callback = one_time_callback

    def __repr__(self):
        return "CallbackItem({}, {}, {}, data={}, one_time_callback={})".format(
            callback_id_from_query(self.id),
            self.chat_id,
            self.action_id,
            type(self.model_data),
            self.one_time_callback
        )


class ICallbackManager(object):
    __metaclass__ = ABCMeta

    id_counter = 100
    COUNTER_RELOOP = int("1" * 20, 2)  # max 20 binary digits

    @abstractmethod
    def create_callback(self, action_id, data, random_id=True):
        pass

    @abstractmethod
    def lookup_chat_bound_callback(self, chat_or_user, callback_data):
        pass

    @abstractmethod
    def peek_action(self, callback_data):
        pass

    @staticmethod
    def create_unique_uuid():
        return str(uuid4())

    @classmethod
    def get_next_id(cls):
        cls.id_counter += 1
        if cls.id_counter > cls.COUNTER_RELOOP:
            cls.id_counter = 0
        return cls.id_counter


class RedisCollectionsCallbackManager(ICallbackManager):

    def __init__(self, persistence=None):
        self._data = dict()
        self.persistence = persistence

    def create_callback(self, action, data, random_id=True):

        cb_id = self.create_unique_uuid() if random_id else self.get_next_id()

        callback = CallbackItem(cb_id, action, data)
        self._data[cb_id] = callback

        return callback

    @classmethod
    def _check_chat(cls, callback_item, chat_id):
        if callback_item.chat_id is None:
            raise ValueError("The requested callback does not have a chat associated. After the "
                             "bot sends a message, the CallbackManager needs to be informed about "
                             "the chat this message was sent to.")
        if callback_item.chat_id != chat_id:
            raise ValueError("The requested callback_data does not belong to this "
                             "chat ({} != {}).".format(callback_item.chat, chat_id))

    def lookup_chat_bound_callback(self, chat_id, callback_id):
        callback_item = self._data.get(callback_id)
        if callback_item:
            self._check_chat(callback_item, chat_id)
            return callback_item.data

    def peek_action(self, callback_data):
        callback_item = self._data.get(callback_data)
        if not callback_item:
            raise CallbackNotFound("The callback {} is not present in "
                                   "this CallbackManager.".format(callback_data))
        return callback_item.action_id

    def set_chat_id(self, callback, chat_id):
        raise NotImplemented  # TODO

    # def set_callback(self, random_id, action_id, data):
    #     self._data[random_id] = dict(action=action_id, data=data)


class DictCallbackManager(ICallbackManager):

    def __init__(self, persistence=None):
        self._data = dict()
        self.persistence = persistence

    def create_callback(self, action_id, data, random_id=True):
        if random_id:
            cb_id = self.create_unique_uuid()
        else:
            cb_id = self.get_next_id()

        callback = CallbackItem(cb_id, action_id, data)
        self._data[cb_id] = callback

        return callback

    @classmethod
    def _check_chat(cls, callback_item, chat_id):
        if callback_item.chat_id is None:
            raise ValueError("The requested callback does not have a chat associated. After the "
                             "bot sends a message, the CallbackManager needs to be informed about "
                             "the chat this message was sent to.")
        if callback_item.chat_id != chat_id:
            raise ValueError("The requested callback_data does not belong to this "
                             "chat ({} != {}).".format(callback_item.chat, chat_id))

    def lookup_callback(self, callback_id):
        callback_item = self._data.get(callback_id)
        if callback_item:
            return callback_item

    def lookup_chat_bound_callback(self, chat_id, callback_id):
        callback_item = self.lookup_callback(callback_id)
        self._check_chat(callback_item, chat_id)
        return callback_item

    def peek_action(self, callback_id):
        callback_item = self._data.get(callback_id)
        if not callback_item:
            raise CallbackNotFound("The callback {} is not present in "
                                   "this CallbackManager.".format(callback_id))
        return callback_item.action_id

    def set_chat_id(self, callback, chat_id):
        raise NotImplemented  # TODO
