import discord
import tempfile
from pagination import Pagination
from database import (
        get_rankings,
        get_session,
        get_user,
        get_or_create_user,
        get_user_rank,
        get_server_config,
        update_server_config,
        get_closest_role,
        )
from ocr import extract_numbers_with_template
from utils import generate_embed


@discord.ext.commands.hybrid_command(name='rankings',
                                     help='Show the battlepower ranking')
async def rankings_command(ctx):
    # Set default page to 1
    interaction = ctx.interaction
    with get_session() as session:
        async def get_page(page: int):
            users = get_rankings(session)
            emb = discord.Embed(
                    title="Battlepower Ranking",
                    description="Ranking of the registered users\n")
            offset = (page-1) * 10
            for user in users[offset:offset+10]:
                # Add rank index
                emb.description += f"**{users.index(user)+1}** - "
                emb.description += f"{user.username} - "
                emb.description += f"{user.battlepower }\n"
            emb.set_author(
                    name=f"Ranking requested by {interaction.user}")
            n = Pagination.compute_total_pages(len(users), 10)
            emb.set_footer(text=f"Page {page} from {n}")
            return emb, n

    await Pagination(interaction, get_page).navegate()


@discord.ext.commands.hybrid_command(
        name='rank',
        description='Check your rank')
async def rank(ctx):
    interaction = ctx.interaction
    with get_session() as session:
        user = get_user(session, interaction.user.id)
        if not user:
            await interaction.response.send_message(
                    'You do not have a rank yet')
            return
        rank = get_user_rank(session, user)
        embed = generate_embed(
                title="Your Rank",
                description="Check your rank in the battlepower ranking",
                color=discord.Color.blue())
        embed.add_field(
                name="Ranking Poisiton", value=rank, inline=False)
        embed.add_field(
                name="Battlepower", value=user.battlepower, inline=False)
        session.commit()
        await interaction.response.send_message(embed=embed)


@discord.ext.commands.hybrid_command(
        name='update_battlepower',
        description='Update your battlepower')
async def update_battlepower(ctx, image: discord.Attachment):
    interaction = ctx.interaction
    if not image.content_type.startswith('image'):
        await interaction.reponse.send_message("Please upload an image")
        return

    with get_session() as session:
        user = get_or_create_user(session, interaction.user)
        server_config = get_server_config(session, interaction.guild.id)
        if not server_config.data.get('battlepower_channel_id'):
            server_config.data[
                    'battlepower_channel_id'] = interaction.channel.id
            update_server_config(session, server_config)
            # Object needs to be refreshed
            server_config = get_server_config(
                    session, interaction.guild.id)
        if interaction.channel.id == server_config.data.get(
                'battlepower_channel_id'):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(await image.read())
                temp.seek(0)
                text = extract_numbers_with_template(temp.name)
                try:
                    text = int(text)
                except ValueError:
                    await interaction.response.send_message(
                            embed=generate_embed(
                                title="Battlepower",
                                description="Could not extract a number from the image",  # noqa
                                color=discord.Color.red())
                            )
                if user.battlepower == text:
                    await interaction.response.send_message(
                            embed=generate_embed(
                                title="Battlepower",
                                description="Battlepower is already **%s**" % text,  # noqa
                                color=discord.Color.red())
                            )
                    return
                user.battlepower = text
                role = get_closest_role(session, text)
                if role:
                    if user.battlepower_role and role != user.battlepower_role:
                        await interaction.user.remove_roles(
                                interaction.guild.get_role(
                                    user.battlepower_role.role_id))
                    user.battlepower_role = role
                    await interaction.user.add_roles(
                            interaction.guild.get_role(role.role_id))
                    embed = generate_embed(
                            title="Battlepower Updated",
                            description="Updated battlepower for @%s (%s) to **%s**\n"  # noqa
                            "You have been given the role **@%s**" % (
                                user.username,
                                user.name,
                                user.battlepower,
                                role.role_name,
                                ),
                            color=discord.Color.green())
                else:
                    embed = generate_embed(
                            title="Battlepower Updated",
                            description="Updated battlepower for @%s (%s) to **%s**" % (  # noqa
                                user.username,
                                user.name,
                                user.battlepower,
                                ),
                            color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
            session.commit()


def ranking_command_setup(client):
    client.add_command(rankings_command)
    client.add_command(rank)
    client.add_command(update_battlepower)
