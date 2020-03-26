# Cards Against Humanity Telegram Bot
Cards Against Humanity (Clone) Telegram Bot v0.5

## Create a Telegram Bot with BotFather
![Tutorial](https://miro.medium.com/max/800/1*-crLu3bHbIYx3kJ0nOomtw.gif)
    
    Copy the token, and paste it in a new file "api_token"
    
## Start the Bot

    conda create -n cah python=3.6
    conda activate cah
    pip install -r requirements.txt
    python main.py
    

# Gameplay

1.  Open the private chat of your newly created telegram bot and write * /start * (every player has to do this)
2.  Add the bot to a telegram group
3.  Write /create in the group, to create a game
4.  Then /join the game (every player has to do this)
5.  /begin the game, interactions take place in the private chat

# *wip Docker

    docker build -t cah_telegram:latest .
    

# Thanks to
    
Telegram Python API  
https://github.com/python-telegram-bot/python-telegram-bot
    
Cards Against Humanity as plain text and JSON  
https://www.crhallberg.com/cah/
