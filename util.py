import re

from telegram import ReplyKeyboardMarkup

from stats import *


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def send_choice(update, context, chat_id, title, choices):
    reply_markup = ReplyKeyboardMarkup(build_menu(choices, n_cols=1), one_time_keyboard=True)
    context.bot.send_message(parse_mode='html', chat_id=chat_id, text=title, reply_markup=reply_markup)


def is_user_czar(game_id, user_id):
    current_game = games[game_id]
    return user_id == current_game["users"][current_game["czar"]]


def format_msg(msg):
    return re.sub(r'[^\S\r\n]{2,}', '', msg)
