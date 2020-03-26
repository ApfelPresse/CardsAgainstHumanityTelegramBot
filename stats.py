import json

# TODO ugly

version = 0.6

commands = {}

decks = {}
with open('deck.json', encoding="utf-8") as jsonfile:
    decks = json.load(jsonfile)

games = {}
user_ids = {}
player_to_private_chat_id = {}
game_stats_default = {
    "max_score": 8,
    "min_players": 2,
    "deck_keys": "Base,CAHe1,CAHe2,CAHe3,CAHe4,CAHe5,CAHe6"
}

# ugly hack
send_return_back_to_game = {}
