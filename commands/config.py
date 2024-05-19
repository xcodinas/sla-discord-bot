import discord
from discord.ext import commands

from database import (
        get_server_config,
        update_server_config,
        get_session,
        )
from utils import generate_embed


@discord.ext.commands.hybrid_command(
        name='set_battlepower_channel',
        description='Set the channel for battlepower updates')
@commands.has_permissions(administrator=True)
async def set_battlepower_channel(ctx, channel: discord.TextChannel):
    interaction = ctx.interaction
    with get_session() as session:
        server_config = get_server_config(
                session, interaction.guild.id)
        server_config.data['battlepower_channel_id'] = (
                channel.id)
        update_server_config(session, server_config)
        embed = generate_embed(
                title='Battlepower Channel Set',
                description='Battlepower channel set to #%s' % (
                    channel.name),
                color=discord.Color.green())
        session.commit()
        await interaction.response.send_message(embed=embed)


def config_command_setup(client):
    client.add_command(set_battlepower_channel)
