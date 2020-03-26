import logging
import os

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from private import *
from util import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def choose_random_black_card(game_id):
    current_game = games[game_id]

    try:
        deck = random.choice(current_game["game_stats"]["deck_keys"].split(","))
    except:
        deck = random.choice(game_stats_default["deck_keys"].split(","))

    card = random.choice(decks[deck]["black"])
    return card


def create_game(update, context, game_id):
    if game_id not in games:
        msg = format_msg(f'''
        Thanks for creating a new game! {crescmoon}

        Other Humans can

        {handshake} send me a **private message** with /start

        {glass} and then join here with /join !''')
        games[game_id] = {
            "users": [],
            "czar": 0,
            "min_players": 2,
            "game_started": False,
            "game_stats": game_stats_default.copy(),
            "cards": {},
            "black_card": 0,
            "scores": {},
            "card_choice": {}
        }
        context.bot.send_message(parse_mode='Markdown', chat_id=game_id, text=msg)


def join(update, context):
    msg_gamestart = format_msg(f'''Enough humans. The game is starting. {point_left}
    Hurry on *back to the private chat* to pick your cards and play {violin} {dice}.''')

    user_id = update.effective_user.id

    if update.effective_chat.type == "private":
        msg = "Forever Alone? Or you want to play with yourself? No? \n" \
              "Just add me o a group and then create a game!"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    if user_id not in user_ids:
        msg = format_msg(f'''
            I dont know you! Human!
            First send me a private message (/start)
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    game_id = update.effective_chat.id
    create_game(update, context, game_id)

    current_game = games[update.effective_chat.id]

    if user_id in current_game["users"]:
        msg = format_msg(f'''
            You've already joined the game
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    current_game["users"].append(user_id)
    current_game["cards"][user_id] = []
    current_game["scores"][user_id] = 0
    current_game["card_choice"][user_id] = []

    msg = f"Human {update.effective_user.first_name} joined the game!! Yeaaaah {grin}!!"
    context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)

    diff_players = current_game["min_players"] - len(current_game["users"])
    if not current_game["game_started"]:
        if diff_players <= 0:
            current_game["game_started"] = True
            context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id,
                                     text=msg_gamestart)
            next_player(update, context)
        else:
            send_waiting_for_players(update, context, game_id, diff_players)
    else:
        """
        use
        msg = format_msg(f'''
            I dont know you! Human!
            First send me a private message (/start)
        ''')
        """

        # group message
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id,
                                 text=f"Welcome to the game! Game started, please wait until next round")

        # private message
        context.bot.send_message(parse_mode='Markdown', chat_id=player_to_private_chat_id[user_id],
                                 text=f"Game started, please wait until next round")


def send_waiting_for_players(update, context, game_id, diff_players):
    if diff_players == 1:
        context.bot.send_message(parse_mode='Markdown', chat_id=game_id,
                                 text=f"{hourglass} {diff_players} player is missing! ")
    else:
        context.bot.send_message(parse_mode='Markdown', chat_id=game_id,
                                 text=f"{hourglass} {diff_players} players are missing!")


def fill_white_cards(game_id):
    current_game = games[game_id]
    max_cards = 10
    deck = "Base"
    for user in current_game["users"]:
        cards = random.sample(decks[deck]["white"], max_cards - len(current_game["cards"][user]))
        current_game["cards"][user] += cards


def next_player(update, context):
    if update.effective_chat.type == "private":
        msg = "Forever Alone? Or you want to play with yourself? No? \n" \
              "Just add me to a group and then create a game!"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    game_id = update.effective_chat.id

    if game_id not in games:
        msg = "Yeah.. Let's begin a game then create one..." \
              "Create a game Huuuman!"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    current_game = games[game_id]

    for user_id in current_game["card_choice"]:
        current_game["card_choice"][user_id] = []

    if len(current_game["users"]) < 1:
        msg = "Get some Friends...or try to join with /join?"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    game_loop(update, context, game_id)


def it_czar(game_id):
    current_game = games[game_id]
    czar_id = current_game["czar"]
    czar_id += 1
    if czar_id >= len(current_game["users"]):
        czar_id = 0
    current_game["czar"] = czar_id


def remove_chosen_cards(game_id):
    current_game = games[game_id]
    for user_id in current_game["users"]:
        choose_card = current_game["card_choice"][user_id]
        cards = current_game["cards"][user_id]
        cards = [card for card in cards if card not in choose_card]
        current_game["cards"][user_id] = cards
        current_game["card_choice"][user_id] = []


def send_score_to_players(update, context, game_id):
    msg = "Scores \n"
    current_game = games[game_id]
    for user_id in current_game["users"]:
        score = current_game["scores"][user_id]
        name = user_ids[user_id]["info"]["first_name"]
        msg += f"{name} - Score {score} \n"
    send_message_to_players(update, context, game_id, msg)


def notify_card_czar(update, context, game_id):
    current_game = games[game_id]
    czar_id = current_game["czar"]
    user_id = current_game["users"][czar_id]
    black_card_text = get_current_black_card(game_id)["text"]
    msg = format_msg(f'''
        You are the card czar, please wait for other players!
        *{black_card_text}*
    ''')
    context.bot.send_message(parse_mode='Markdown', chat_id=player_to_private_chat_id[user_id], text=msg)


def reset_game(game_id):
    current_game = games[game_id]
    for user_id in current_game["users"]:
        current_game["scores"][user_id] = 0
        current_game["card_choice"][user_id] = []
        current_game["cards"][user_id] = []


def game_loop(update, context, game_id):
    current_game = games[game_id]

    diff_players = current_game["min_players"] - len(current_game["users"])
    if diff_players > 0:
        send_waiting_for_players(update, context, game_id, diff_players)
        return

    remove_chosen_cards(game_id)
    it_czar(game_id)

    send_score_to_players(update, context, game_id)
    if game_over(context, game_id, update):
        reset_game(game_id)

    fill_white_cards(game_id)
    current_game["black_card"] = choose_random_black_card(game_id)

    notify_card_czar(update, context, game_id)
    # send_black_card(update, context, game_id)

    send_cards_choice_to_all_players(update, context, game_id)


def game_over(context, game_id, update):
    current_game = games[game_id]
    for user_id in current_game["users"]:
        score = current_game["scores"][user_id]
        name = user_ids[user_id]["info"]["first_name"]

        try:
            max_score = current_game["game_stats"]["max_score"]
        except:
            max_score = game_stats_default["max_score"]

        if score >= max_score:
            msg = format_msg(f'''
                Player {name} wins the game!
                Score {score}
            ''')
            send_message_to_players(update, context, game_id, msg)
            return True
    return False


def send_cards_choice_to_all_players(update, context, game_id):
    current_game = games[game_id]
    for user_id in current_game["users"]:
        current_game["card_choice"][user_id] = []
        if is_user_czar(game_id, user_id):
            continue
        send_cards_choice_to_user(update, context, game_id, user_id)


def czar_round(game_id):
    current_game = games[game_id]
    how_many_cards_to_choose = get_current_black_card(game_id)["pick"]
    how_many_players = len(current_game["card_choice"].values()) - 1
    how_many_choose_at_the_moment = len(sum(current_game["card_choice"].values(), []))
    return how_many_choose_at_the_moment == (how_many_players * how_many_cards_to_choose)


def get_current_black_card(game_id):
    current_game = games[game_id]
    black_card_id = current_game["black_card"]
    return decks["blackCards"][black_card_id]


def send_black_card(update, context, game_id):
    current_black = get_current_black_card(game_id)
    pick = current_black["pick"]
    msg = "*" + current_black["text"] + "*\n"
    msg += f"Pick {pick} Card(s)!"
    context.bot.send_message(parse_mode='Markdown', chat_id=game_id, text=msg)


def send_message_to_players(update, context, game_id, msg):
    current_game = games[game_id]
    for user in current_game["users"]:
        try:
            chat_id = player_to_private_chat_id[user]
            context.bot.send_message(parse_mode='Markdown', chat_id=chat_id, text=msg)
        except:
            pass


def create_cards_choice_czar_dict(game_id):
    current_game = games[game_id]
    res = {}
    for user_id in current_game["card_choice"]:
        cards = current_game["card_choice"][user_id]
        choices = list(map(decks["whiteCards"].__getitem__, cards))
        str_choice = " - ".join(choices)
        res[user_id] = str_choice
    return res


def create_cards_choice_czar(game_id):
    button_list = list(create_cards_choice_czar_dict(game_id).values())
    random.shuffle(button_list)
    return button_list


def send_choice_to_czar(update, context, game_id):
    current_game = games[game_id]
    czar_id = current_game["czar"]
    user_id = current_game["users"][czar_id]

    black_card_id = current_game["black_card"]
    title = decks["blackCards"][black_card_id]["text"]

    send_return_back_to_game[user_id].insert(0, game_id)

    button_list = create_cards_choice_czar(game_id)
    send_choice(update, context, player_to_private_chat_id[user_id], title, button_list)


def send_cards_choice_to_user(update, context, game_id, user_id):
    current_game = games[game_id]

    button_list = [decks["whiteCards"][card] for card in current_game["cards"][user_id] if
                   card not in current_game["card_choice"][user_id]]
    black_card = get_current_black_card(game_id)
    pick = black_card["pick"]
    title = black_card["text"] + f" Pick {pick} !"

    # to know which choice belongs to which game
    # ist a ugly solution
    send_return_back_to_game[user_id].insert(0, game_id)

    send_choice(update, context, player_to_private_chat_id[user_id], title, button_list)


def leave(update, context):
    game_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        msg = "Leaving me?? \n" \
              "You can't leave me!"
        context.bot.send_message(chat_id=game_id, text=msg)

    user_id = update.effective_user.id
    # try:
    if game_id in games:
        current_game = games[game_id]

        if user_id in current_game["users"]:
            current_game["users"].remove(user_id)
            current_game["cards"].pop(user_id, None)
            current_game["scores"].pop(user_id, None)
            current_game["card_choice"].pop(user_id, None)

            chat_id = player_to_private_chat_id[user_id]
            msg = "You left the game!"
            context.bot.send_message(chat_id=chat_id, text=msg)

            # reset game if someone leafs the game
            for user in current_game["card_choice"]:
                current_game["card_choice"][user] = []

            game_loop(update, context, game_id)
        else:
            msg = "You are not part of the game!"
            context.bot.send_message(chat_id=game_id, text=msg)
    else:
        msg = "There is no game you can leave!"
        context.bot.send_message(chat_id=game_id, text=msg)


# except:
#    msg = "Something went wrong, but I am sure you left the game.."
#    context.bot.send_message(chat_id=game_id, text=msg)


def destroy(update, context):
    if update.effective_chat.type == "private":
        msg = format_msg(f'''
            Destroying you...?
            What would be the point of that?
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return
    game_id = update.effective_chat.id
    if game_id in games:
        games.pop(game_id, None)
        msg = format_msg(f'''
                    thx
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
    else:
        msg = format_msg(f'''
            Nothing happened!
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)


def status(update, context):
    game_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        msg = format_msg(f'''
                Only in Groups!
        ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    if game_id not in games:
        msg = format_msg(f'''
                    There is no game!
                ''')
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    current_game = games[game_id]
    msg = f"*Status* \n\n"

    czar_rou = czar_round(game_id)
    if czar_rou:
        msg += "The czar has to choose a card! \n\n"
    else:
        msg += "Some players are still choosing! \n\n"

    how_many_cards_to_choose = get_current_black_card(game_id)["pick"]
    for user_id in current_game['users']:
        name = user_ids[user_id]["info"]["first_name"]
        czar = is_user_czar(game_id, user_id)
        how_many_cards_did_player_choose = len(current_game["card_choice"][user_id])
        is_choosing = how_many_cards_did_player_choose < how_many_cards_to_choose
        if czar:
            msg += f"{name} is card czar! \n"
        else:
            if is_choosing:
                msg += f"{name}, is choosing \n"
            else:
                msg += f"{name}, has chosen \n"

    context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)


def load_api_token():
    """
    :return: Telegram API Token from BotFather
    """
    filename = 'api_token'
    if os.path.isfile(filename):
        with open('api_token', 'r') as file:
            api_token = file.read().replace("\n", "")
            return api_token
    return ""


def main():
    api_token = load_api_token()
    if not api_token:
        api_token = os.environ['API_TOKEN']
    updater = Updater(token=api_token, use_context=True)
    dispatcher = updater.dispatcher

    commands = {
        "join": {
            "method": join,
            "short_desc": "",
            "long_desc": ""
        },
        "start": {
            "method": start,
            "short_desc": "",
            "long_desc": ""
        },
        "next": {
            "method": next_player,
            "short_desc": "",
            "long_desc": ""
        },
        "leave": {
            "method": leave,
            "short_desc": "",
            "long_desc": ""
        },
        "destroy": {
            "method": destroy,
            "short_desc": "",
            "long_desc": ""
        },
        "status": {
            "method": status,
            "short_desc": "",
            "long_desc": ""
        }
    }
    [dispatcher.add_handler(CommandHandler(command, commands[command]["method"])) for command in commands]
    dispatcher.add_handler(MessageHandler(Filters.text, callback))
    updater.start_polling()


if __name__ == "__main__":
    main()
