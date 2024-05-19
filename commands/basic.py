import discord
from discord.ext import commands


@discord.ext.commands.hybrid_command(
        name='ping',
        description='Check if the bot is responding')
@commands.has_permissions(administrator=True)
async def ping(ctx, channel: discord.TextChannel):
    interaction = ctx.interaction
    await interaction.response.send_message("Pong")


def basic_command_setup(client):
    client.add_command(ping)
