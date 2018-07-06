from collections import Iterable
from typing import Callable, Generic, TypeVar

import telegram
import telegram.flow


class ViewModel(object):
    pass


class RerouteToAction(object):
    def __init__(self, origin_action: 'Action', view_model=None, new_state=None):
        self.origin_action = origin_action
        self.new_state = new_state

        if view_model is None:
            if origin_action.model_type:
                # Make sure the view model is always available
                view_model = origin_action.model_type()
        elif not isinstance(view_model, origin_action.model_type):
            raise TypeError("Invalid model type: Action requires {}, but {} was supplied.".format(
                origin_action.model_type.__class__.__name__,
                type(view_model)
            ))

        self.view_model = view_model


class ActionRepository(object):
    @classmethod
    def get_unused_actions(cls, actual_usage_ids: list):
        return
        print(actual_usage_ids)
        unused = []
        print(cls.__name__)
        for k, v in cls.__dict__.items():
            print(k, v)
            # TODO XXX
            try:
                actual_usage_ids.index(v.id)
            except ValueError:
                unused.append((k, v))

        return unused


T = TypeVar('T', bound=ViewModel)


class Action(Generic[T]):
    def __init__(self,
                 id=None,
                 caption: Callable[[T], str] = None,
                 commands=None,
                 model_type: T = None,
                 check_types=None,
                 buttons=True,
                 inline_buttons=True):

        self._caption = caption
        if commands:
            commands = commands if isinstance(commands, Iterable) else [commands]
        self.commands = commands
        # self.switch_inline_query = switch_inline_query  TODO: implement
        # self.description = description  TODO: implement
        # self.help_text = help_text  TODO: implement
        self.model_type = model_type

        from telegram.flow import perform_argument_checks
        self.check_types = (check_types
                            if check_types is not None
                            else telegram.flow.perform_argument_checks)

        self.buttons = buttons
        self.inline_buttons = inline_buttons

        if id is not None:
            self.id = id
        else:
            self.id = self.__hash__()

    def get_handler(self, callback, filters=None):
        from telegram.ext import ActionHandler
        return ActionHandler(self,
                             callback,
                             filters=filters,
                             pass_update_queue=False,
                             pass_job_queue=False,
                             pass_user_data=False,
                             pass_chat_data=False)

    def get_caption(self, view_data=None):
        if callable(self._caption):
            if view_data is None:
                return self._caption()
            else:
                return self._caption(view_data)
        else:
            return self._caption

    def check_model_consistency(self, provided):
        # TODO is there still anything to do?
        return True

    def __call__(self, view_model):
        return RerouteToAction(self, view_model)


def get_action_id(action):
    if isinstance(action, Action):
        return str(action.id)
    return str(action)
