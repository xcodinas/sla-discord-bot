import discord
import tempfile
from ocr import extract_numbers_with_template
from database import (
        get_user,
        get_server_config,
        update_user,
        create_user,
        update_server_config,
        get_session,
        )


class DiscordBot:
    def __init__(self, token=None):
        intents = discord.Intents.default()
        intents.message_content = True

        self.client = discord.Client(
                token=token,
                intents=intents,
                )

        if not token:
            raise ValueError('Token is required')
        self.token = token

    def run(self):
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            with get_session() as session:
                if message.author == self.client.user:
                    return

                user = get_user(session, message.author.id)
                if not user:
                    create_user(
                            session,
                            discord_id=message.author.id,
                            username=message.author.name,
                            name=message.author.display_name,
                            battlepower=0,
                            )
                    user = get_user(session, message.author.id)
                if user.name != message.author.display_name:
                    user.name = message.author.display_name

                server_config = get_server_config(session, message.guild.id)
                if not server_config.data.get('battlepower_channel_name'):
                    server_config.data['battlepower_channel_name'] = 'bc-proof'
                    print(server_config.data)
                    update_server_config(session, server_config)
                    # Object needs to be refreshed
                    server_config = get_server_config(
                            session, message.guild.id)

                if message.channel.name == server_config.data.get(
                        'battlepower_channel_name') and message.attachments:
                    for attachment in message.attachments:
                        with tempfile.NamedTemporaryFile() as temp:
                            temp.write(await attachment.read())
                            temp.seek(0)
                            text = extract_numbers_with_template(temp.name)
                            try:
                                text = int(text)
                            except ValueError:
                                await message.channel.send(
                                        "Could not extract battlepower from image"  # noqa
                                        )
                            user.battlepower = text
                            await message.channel.send(
                                    "Updated battlepower for %s (@%s) to **%s**" % (  # noqa
                                        user.name,
                                        user.username,
                                        user.battlepower,
                                        )
                                    )

                if message.content == 'ping':
                    await message.channel.send('pong')
                update_user(session, user)

        self.client.run(self.token)
