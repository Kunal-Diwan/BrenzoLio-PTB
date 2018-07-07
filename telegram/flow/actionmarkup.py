from itertools import chain

from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup


# TODO REFACTOR: move into ReplyMarkup class
def resolve_action_markup(callback_manager, reply_markup, chat_id=None):
    if chat_id:
        # Make a best effort to use the provided chat_id, but it will be inserted from the outside after the update
        # has been sent. This only needs to happen when the markup is bound to a specific chat, i.e. when
        # `callback_manager.lookup_chat_bound_callback` is used.
        try:
            chat_id = int(chat_id)
        except TypeError:
            chat_id = None

    callbacks = []
    buttons = []
    if isinstance(reply_markup, InlineKeyboardMarkup):
        buttons = reply_markup.inline_keyboard
        is_inline = True
    elif isinstance(reply_markup, ReplyKeyboardMarkup):
        buttons = reply_markup.keyboard
        is_inline = False

    from telegram.ext import ActionButton
    buttons = [b for b
               in chain.from_iterable(buttons)
               if isinstance(b, ActionButton)]

    for n, button in enumerate(buttons):
        # noinspection PyUnboundLocalVariable
        button.is_inline = is_inline
        callback = button.insert_callback(callback_manager)

        callback.chat_id = chat_id

        callbacks.append(callback)

    return callbacks
