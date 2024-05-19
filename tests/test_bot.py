import discord
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord.ext.test as dpytest
from bot import DiscordBot
from commands.basic import ping
from commands.config import set_battlepower_channel
from commands.rankings import update_battlepower
from commands.roles import add_role
from utils import generate_embed


class TestBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Run dB migrations

        # Initialize the bot with a test token
        self.bot = DiscordBot(token="test")
        dpytest.configure(self.bot.client)

        # Create a test user and guild
        self.user = dpytest.backend.make_user("pondere", self.bot.client.user)
        self.guild = dpytest.backend.make_guild(name="Test Guild")

        # Create roles and channels in the test guild
        self.channel = dpytest.backend.make_text_channel(
                "bc-proof", self.guild)
        self.member = await dpytest.member_join(self.guild, self.user)

        self.roles = {
                "E-Rank": 10000,
                "D-Rank": 25000,
                "C-Rank": 50000,
                "B-Rank": 100000,
                "A-Rank": 150000,
                "S-Rank": 200000,
                "National Level Hunter": 250000,
                }
        self.dc_roles = {}
        roles = self.roles.keys()
        for role in roles:
            r = dpytest.backend.make_role(role, self.guild)
            self.dc_roles[role] = r

        # Await the bot to be fully ready
        await self.bot.client._async_setup_hook()

    async def asyncTearDown(self):
        await dpytest.empty_queue()

    @patch("discord.ext.commands.Context")
    async def test_ping_command(self, mock_ctx):
        # Setup mock interaction and context
        mock_interaction = AsyncMock()
        mock_ctx.interaction = mock_interaction
        mock_ctx.channel = self.channel
        mock_ctx.guild = self.guild

        # Run the command
        await ping(mock_ctx, channel=self.channel)

        # Assert the interaction response
        mock_interaction.response.send_message.assert_called_once_with("Pong")

    @patch("discord.ext.commands.Context")
    async def test_set_channel_command(self, mock_ctx):
        # Setup mock interaction and context
        mock_interaction = AsyncMock()
        mock_ctx.interaction = mock_interaction
        mock_ctx.channel = self.channel
        mock_ctx.channel.id = self.channel.id
        mock_ctx.guild = self.guild
        mock_ctx.guild.id = self.guild.id
        mock_interaction.guild = mock_ctx.guild

        # Run the command
        await set_battlepower_channel(mock_ctx, channel=self.channel)

        # Assert the interaction response
        mock_interaction.response.send_message.assert_called_once_with(
                embed=generate_embed(
                    title='Battlepower Channel Set',
                    description='Battlepower channel set to #%s' % (
                        self.channel.name),
                    color=discord.Color.green())
                )

    @patch("discord.ext.commands.Context")
    async def test_add_role(self, mock_ctx):
        # Setup mock interaction and context
        mock_interaction = AsyncMock()
        mock_ctx.interaction = mock_interaction
        mock_ctx.channel = self.channel
        mock_ctx.guild = self.guild
        mock_ctx.guild.id = self.guild.id
        mock_interaction.guild = mock_ctx.guild

        # Run the command
        for role_name, battlepower in self.roles.items():
            await add_role(
                    mock_ctx, dc_role=self.dc_roles[role_name],
                    battlepower=battlepower)

            # Assert the interaction response
            mock_interaction.response.send_message.assert_called_with(
                    embed=generate_embed(
                        title='Role added',
                        description="The role %s has been added to the database, it will be given when user reaches %s battlepower." % (  # noqa
                            role_name, battlepower),
                        color=discord.Color.green())
                    )

    @patch("commands.rankings.extract_numbers_with_template",
           new_callable=MagicMock)
    @patch("discord.ext.commands.Context")
    async def test_update_battlepower(self, mock_ctx, mock_extract_numbers):
        # Setup mock interaction and context
        mock_interaction = AsyncMock()
        mock_ctx.interaction = mock_interaction
        mock_ctx.author = self.user
        mock_ctx.author.id = self.user.id
        mock_ctx.channel = self.channel
        mock_ctx.guild = self.guild
        mock_ctx.guild.id = self.guild.id
        mock_interaction.guild = mock_ctx.guild
        mock_interaction.user = discord.Member
        mock_interaction.user.name = self.user.name
        mock_interaction.user.display_name = self.user.display_name
        mock_interaction.user.get_roles = AsyncMock()
        mock_interaction.user.id = self.user.id
        mock_interaction.channel.id = self.channel.id
        mock_interaction.user.add_roles = AsyncMock()
        mock_interaction.user.remove_roles = AsyncMock()

        image = dpytest.backend.make_attachment(
                filename=Path("img/image.png"),
                )
        image.content_type = "image/png"
        for role_name, battlepower in self.roles.items():
            mock_extract_numbers.return_value = battlepower
            await update_battlepower(mock_ctx, image=image)
            mock_interaction.response.send_message.assert_called_with(
                    embed=generate_embed(
                        title="Battlepower Updated",
                        description="Updated battlepower for @%s (%s) to **%s**\n"  # noqa
                        "You have been given the role **@%s**" % (
                            self.user.name,
                            self.user.name,
                            battlepower,
                            role_name,
                            ),
                        color=discord.Color.green())
                    )


if __name__ == '__main__':
    unittest.main()
