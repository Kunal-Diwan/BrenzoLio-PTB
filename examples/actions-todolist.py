#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced example demonstrating a todolist app with a keyboard menu

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
from functools import partial
from dataclasses import dataclass
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode

from telegram.ext import (Action, ActionHandler, ActionRepository, ActionButton, CallbackContext, CommandHandler,
                          ConversationHandler, Filters, MessageHandler, RerouteToAction, Updater, ViewModel)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


### region Classes

class TodoItem(object):
    def __init__(self, title):
        self.title = title
        self.done = False

    def __str__(self):
        return ('✅' if self.done else '📋') + ' ' + self.title


# endregion
### region Actions and States

# region Callback Parameter Definitions

@dataclass
class ItemModel(ViewModel):
    item: TodoItem


@dataclass
class TextModel(ViewModel):
    text: str = None


# endregion

class Actions(ActionRepository):
    ADD_ITEMS = Action('add_init', caption='Add ➕', commands=['add', 'todo'])
    REMOVE_ITEMS = Action('remove_init', caption='Remove ➖', commands=['rem', 'remove', 'del'])
    DELETE_ITEM = Action('delete',
                         caption=lambda cbdata: '🗑 {}'.format(cbdata.item.title),
                         model_type=ItemModel)
    TOGGLE_DONE = Action('done',
                         caption=lambda cbdata: str(cbdata.item),
                         model_type=ItemModel)
    START = Action('start', caption='🔙 Cancel', commands=['start'], model_type=TextModel)


class States:
    ADD_ITEMS = 1


# endregion
### region ActionButton Menu Setup
# Make toggleable property whether to use either inline, or regular keyboard buttons
Markup = InlineKeyboardMarkup


def toggle_keyboard(update, context):
    global Markup
    if Markup == InlineKeyboardMarkup:
        Markup = partial(ReplyKeyboardMarkup, resize_keyboard=True)
        set_to = 'reply'
    else:
        Markup = InlineKeyboardMarkup
        set_to = 'inline'

    reply_markup = ReplyKeyboardRemove()
    update.message.reply_text(
        "Menu layout set to {} buttons.".format(set_to),
        reply_markup=reply_markup)
    context.job_queue.run_once(lambda *args: start(update, context), 0.5)


def get_cancel_button():
    return ActionButton.from_action(Actions.START)


# endregion

def send_or_edit(update, text, reply_markup=None):
    if update.callback_query:
        # Edit the message if a button was pressed
        update.effective_message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif update.message:
        # Send a message if a command was sent
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )


def start(update, context: CallbackContext[TextModel]):
    todo_items = context.user_data.setdefault("todo", [])

    if context.view_model is None:
        context.view_model = TextModel("Your Todo List")

    keyboard = [[
        ActionButton.from_action(Actions.ADD_ITEMS),
        ActionButton.from_action(Actions.REMOVE_ITEMS),
    ]]

    for t in todo_items:
        # Create new keyboard row for every item
        keyboard.append(
            [ActionButton.from_action(Actions.TOGGLE_DONE, ItemModel(item=t))]
        )

    reply_markup = Markup(keyboard)

    send_or_edit(update, context.view_model.text, reply_markup)

    return ConversationHandler.END


def add_items_init(update, context):
    keyboard = [[get_cancel_button()]]
    reply_markup = Markup(keyboard)
    send_or_edit(
        update,
        "📝 Please send me what you need to do",
        reply_markup=reply_markup
    )
    return States.ADD_ITEMS


def add_item(update, context):
    item = TodoItem(update.message.text)

    context.user_data["todo"].append(item)

    return RerouteToAction(Actions.START, TextModel("Item added."))


def remove_items_init(update, context: CallbackContext[ItemModel]):
    keyboard = [[get_cancel_button()]]
    todo_items = context.user_data["todo"]

    for t in todo_items:
        keyboard.append(
            [ActionButton.from_action(Actions.DELETE_ITEM, ItemModel(item=t))]
        )

    reply_markup = Markup(keyboard)

    send_or_edit(update,
                 "Please select the item to remove",
                 reply_markup=reply_markup)

    return States.ADD_ITEMS


def delete_item(update, context: CallbackContext[ItemModel]):
    item = context.view_model.item
    todo_items = context.user_data['todo']

    todo_items.remove(item)

    return RerouteToAction(Actions.START, TextModel("{} deleted.".format(item.title)))


def toggle_done_state(update, context: CallbackContext[ItemModel]):
    item = context.view_model.item
    item.done = not item.done

    return RerouteToAction(Actions.START, TextModel(
        "{} set to {}.".format(item, 'done' if item.done else 'unfinished')
    ))


# def shareable_add_item_link(update, context, item_to_add):
#     update.message.reply_text("Coming soon")
#     raise NotImplemented  # TODO

def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("287953069:AAHfuHYgopkZu9CEIlxoNOzvWYxajyFuKAs", use_context=True)

    dp = updater.dispatcher

    add_item_handler = ConversationHandler(
        entry_points=[ActionHandler(Actions.ADD_ITEMS, add_items_init)],
        states={
            States.ADD_ITEMS: [
                MessageHandler(Filters.text, add_item),
            ]
        },
        fallbacks=[ActionHandler(Actions.START, start)]
    )
    dp.add_handler(add_item_handler)

    dp.add_handler(ActionHandler(Actions.REMOVE_ITEMS, remove_items_init))
    dp.add_handler(ActionHandler(Actions.DELETE_ITEM, delete_item))
    dp.add_handler(ActionHandler(Actions.TOGGLE_DONE, toggle_done_state))
    dp.add_handler(ActionHandler(Actions.START, start))

    dp.add_handler(CommandHandler("toggle", toggle_keyboard))

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
