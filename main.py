from emoji import emojize
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

from private import *
from util import *

def choose_random_black_card(game_id):
    current_game = games[game_id]

    try:
        deck = random.choice(current_game["game_stats"]["deck_keys"].split(","))
    except:
        deck = random.choice(game_stats_default["deck_keys"].split(","))

    card = random.choice(decks[deck]["black"])
    return card


def create(update, context):
    if update.effective_chat.type == "private":
        msg = "Forever Alone? Or you want to play with yourself? No? \n" \
              "Just add me o a group and then create a game!"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    if update.effective_chat.id in games:
        msg = "Human!! A game has already been created.. Just Join the Game!"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)
        return

    settings = {}
    try:
        for arg in context.args:
            split = arg.split("=")
            key = split[0]
            value = split[1]
            settings[key] = value
    except:
        pass

    msg = "Thanks for creating a new game! Other Humans should write me a private messsage /start and can than join the game with /join !"
    game_id = update.effective_chat.id
    games[game_id] = {
        "users": [],
        "czar": 0,
        "game_stats": game_stats_default.copy(),
        "cards": {},
        "black_card": 0,
        "scores": {},
        "card_choice": {}
    }

    games[game_id]["game_stats"].update(settings)

    context.bot.send_message(parse_mode='Markdown', chat_id=game_id, text=msg)


def join(update, context):
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

    if update.effective_chat.id not in games:
        unamused = emojize(":unamused:", use_aliases=True)
        msg = f"Ohh Human {unamused} \n" \
              "First you have to **/create** a game, then you can join one! \n" \
              "Sounds simple?"
        context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)

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

    grin = emojize(":grin:", use_aliases=True)
    msg = f"Human {update.effective_user.first_name} joined the game!! Yeaaaah {grin}!!"
    context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)


def fill_players_white_cards(game_id):
    current_game = games[game_id]
    max_cards = 10
    deck = "Base"
    for user in current_game["users"]:
        cards = random.sample(decks[deck]["white"], max_cards - len(current_game["cards"][user]))
        current_game["cards"][user] += cards


def begin(update, context):
    if update.effective_chat.type == "private":
        msg = "Forever Alone? Or you want to play with yourself? No? \n" \
              "Just add me o a group and then create a game!"
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

    remove_chosen_cards(game_id)
    it_czar(game_id)

    send_score_to_players(update, context, game_id)
    if game_over(context, game_id, update):
        reset_game(game_id)

    fill_players_white_cards(game_id)
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
    try:
        current_game = games[game_id]

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
    except:
        msg = "Something went wrong, but I am sure you left the game.."
        context.bot.send_message(chat_id=game_id, text=msg)


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


# ['Base', 'CAHe1', 'CAHe2', 'CAHe3', 'CAHe4', 'CAHe5', 'CAHe6', 'greenbox', '90s', 'Box', 'fantasy', 'food', 'science', 'www', 'hillary', 'trumpvote', 'trumpbag', 'xmas2012', 'xmas2013', 'PAXE2013', 'PAXP2013', 'PAXE2014', 'PAXEP2014', 'PAXPP2014', 'PAX2015', 'HOCAH', 'reject', 'reject2', 'Canadian', 'misprint', 'apples', 'crabs', 'matrimony', 'c-tg', 'c-admin', 'c-anime', 'c-antisocial', 'c-equinity', 'c-homestuck', 'c-derps', 'c-doctorwho', 'c-eurovision', 'c-fim', 'c-gamegrumps', 'c-golby', 'GOT', 'CAHgrognards', 'HACK', 'Image1', 'c-ladies', 'c-imgur', 'c-khaos', 'c-mrman', 'c-neindy', 'c-nobilis', 'NSFH', 'c-northernlion', 'c-ragingpsyfag', 'c-stupid', 'c-rt', 'c-rpanons', 'c-socialgamer', 'c-sodomydog', 'c-guywglasses', 'c-vewysewious', 'c-vidya', 'c-xkcd', 'order']

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
        msg += "Czar has to choose a Card! \n"
    else:
        msg += "Players have to chose their cards! \n"

    how_many_cards_to_choose = get_current_black_card(game_id)["pick"]
    for user_id in current_game['users']:
        name = user_ids[user_id]["info"]["first_name"]
        czar = is_user_czar(game_id, user_id)
        how_many_cards_did_player_choose = len(current_game["card_choice"][user_id])
        is_choosing = how_many_cards_did_player_choose < how_many_cards_to_choose
        if czar:
            msg += f"{name} is card czar! \n"
        else:
            msg += f"{name}, is_choosing={is_choosing} \n"

    context.bot.send_message(parse_mode='Markdown', chat_id=update.effective_chat.id, text=msg)


def main():
    with open('api_token', 'r') as file:
        api_token = file.read()
        updater = Updater(token=api_token, use_context=True)
        print(api_token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('create', create)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('join', join)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('begin', begin)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('leave', leave)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('destroy', destroy)
    dispatcher.add_handler(start_handler)
    start_handler = CommandHandler('status', status)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, callback))

    updater.start_polling()


if __name__ == "__main__":
    main()
