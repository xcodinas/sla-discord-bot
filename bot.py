import discord
from discord.ext import commands
from database import (
        get_session,
        get_or_create_user,
        update_user,
        )
from commands.rankings import ranking_command_setup
from commands.config import config_command_setup
from commands.roles import roles_command_setup
from commands.basic import basic_command_setup


class DiscordBot:
    def __init__(self, token=None):
        intents = discord.Intents.default()
        intents.message_content = True

        self.client = commands.Bot(command_prefix='!', intents=intents)

        self.set_commands()

        if not token:
            raise ValueError('Token is required')
        self.token = token

    def set_commands(self):
        # Rankings
        ranking_command_setup(self.client)
        config_command_setup(self.client)
        roles_command_setup(self.client)
        basic_command_setup(self.client)

    def run(self):
        with get_session() as session:
            @self.client.event
            async def on_ready():
                # Recheck if new commands are added
                await self.client.tree.sync()
                print(f'Logged in as {self.client.user}')

            @self.client.event
            async def on_message(message):
                if message.author == self.client.user:
                    return
                # If is another bot, ignore
                if message.author.bot:
                    return

                user = get_or_create_user(session, message.author)
                update_user(session, user)
                session.commit()

        self.client.run(self.token)
