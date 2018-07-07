import re

from telegram import Update
from telegram.ext import Handler
from telegram.flow.action import get_action_id


class InlineQueryActionHandler(Handler):
    """Handler class to handle Telegram callback queries. Optionally based on a regex.

    Read the documentation of the ``re`` module for more information.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pattern (:obj:`str` | `Pattern`): Optional. Regex pattern to test
            :attr:`telegram.CallbackQuery.data` against.
        pass_groups (:obj:`bool`): Optional. Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Optional. Determines whether ``groupdict``. will be passed to
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

    Args:
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
        pattern (:obj:`str` | `Pattern`, optional): Regex pattern. If not ``None``, ``re.match``
            is used on :attr:`telegram.CallbackQuery.data` to determine if an update should be
            handled by this handler.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is ``False``
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is ``False``
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.

    """

    def __init__(self,
                 action,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pattern=None,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(InlineQueryActionHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

        self.action_id = get_action_id(action)
        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, update, dispatcher):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update) and update.inline_query:

            # TODO: check the obfuscated encoded thingy

            if update.inline_query.id != self.action_id:
                return False
            if self.pattern:
                if update.inline_query.query:
                    match = re.match(self.pattern, update.inline_query.query)
                    if match:
                        return match
            else:
                return True

    def collect_optional_args(self, dispatcher, update=None, check_result=None):
        optional_args = super(InlineQueryActionHandler, self).collect_optional_args(
            dispatcher, update, check_result)
        if self.pattern:
            if self.pass_groups:
                optional_args['groups'] = check_result.groups()
            if self.pass_groupdict:
                optional_args['groupdict'] = check_result.groupdict()
        return optional_args

    def collect_additional_context(self, context, update, dispatcher, check_result):
        if self.pattern:
            context.match = check_result

        user_id = update.effective_user.id
        callback_item = dispatcher.callback_manager.lookup_chat_bound_callback(
            user_id, update.callback_query.id)

        context.view_model = callback_item.model_data
