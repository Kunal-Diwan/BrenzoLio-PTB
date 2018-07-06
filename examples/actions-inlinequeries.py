#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Advanced example demonstrating a todolist app with a keyboard menu

# This program is dedicated to the public domain under the CC0 license.
"""
import logging

from telegram import ParseMode
from telegram.ext import (Action, ActionButton, ActionHandler, ActionRepository, CallbackContext, CommandHandler,
                          ConversationHandler, Filters, MessageHandler, Updater)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# endregion

class Actions(ActionRepository):
    ADD_ITEMS = Action('add_init', caption='Add ➕', commands=['add', 'todo'])


class States:
    ADD_ITEMS = 1


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
