# Cards Against Humanity Telegram Bot
![](logo.jpg "")

Cards Against Humanity (Clone) Telegram Bot v0.8

## Create a Telegram Bot with BotFather
![Tutorial](https://miro.medium.com/max/800/1*-crLu3bHbIYx3kJ0nOomtw.gif)
    
    Copy the token, and paste it in a new file "api_token"
    
## (Opt1) Start the Bot local

    conda create -n cah python=3.6
    conda activate cah
    pip install -r requirements.txt
    python main.py
    
## (Opt2) Docker
    
    docker run -d --env API_TOKEN=<API-TOKEN> apfelpresse/cah_telegram:latest
    
## (Opt3) Docker-Compose
    
    version: '3'

    services:
      CAH_Bot:
        image: "cah_telegram:latest"
        environment:
          API_TOKEN: "<API-TOKEN>"

# Gameplay

1.  Open the private chat of your newly created telegram bot and write * /start * (every player has to do this)
2.  Add the bot to a telegram group
3.  Then /join the game

# Thanks to
    
Telegram Python API  
https://github.com/python-telegram-bot/python-telegram-bot
    
Cards Against Humanity as plain text and JSON  
https://www.crhallberg.com/cah/
