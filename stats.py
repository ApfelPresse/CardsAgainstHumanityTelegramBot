import json

version = 0.4

decks = {}
with open('deck.json') as jsonfile:
    decks = json.load(jsonfile)

games = {}
user_ids = {}
player_to_private_chat_id = {}
game_stats_default = {
    "max_score": 8,
    "deck_keys": "Base,CAHe1,CAHe2,CAHe3,CAHe4,CAHe5,CAHe6"
}

# ugly hack
send_return_back_to_game = {}
