import os
from bot import DiscordBot

token = os.environ.get('BOT_TOKEN')

bot = DiscordBot(token)
bot.run()
