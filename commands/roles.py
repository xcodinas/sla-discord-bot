import discord
from database import get_session, get_or_create_role, get_roles
from utils import generate_embed


@discord.ext.commands.hybrid_command(
        name='add_battlepower_role',
        help='Add a rank to check the battlepower')
async def add_role(ctx, dc_role: discord.Role, battlepower):
    # Get the discord server roles, search for the one with the prompt name
    # and add it to the db
    # Usage example
    # /add_battlepower_role "Role name" 1000
    with get_session() as session:
        role = get_or_create_role(
                session, ctx.guild.id, dc_role)
        role.required_battlepower = battlepower
        session.commit()
    embed = generate_embed(
            title="Role added",
            description="The role %s has been added to the database, it will be given when user reaches %s battlepower." % (  # noqa
                dc_role.name, battlepower),
            color=discord.Color.green())
    session.commit()
    await ctx.interaction.response.send_message(embed=embed)


@discord.ext.commands.hybrid_command(
        name='remove_battlepower_role',
        help='Remove a rank to check the battlepower')
async def remove_role(ctx, role_name):
    # Get the discord server roles, search for the one with the prompt name
    # and remove it from the db
    # Usage example
    # /remove_battlepower_role "Role name"
    dc_role = next(
            (role for role in ctx.guild.roles if role.name == role_name), None)
    if not dc_role:
        embed = generate_embed(
                title="Role not found",
                description="Role %s not found in the server" % role_name,
                color=discord.Color.red())
        await ctx.interaction.response.send_message(embed=embed)
        return

    with get_session() as session:
        role = get_or_create_role(
                session, ctx.guild.id, dc_role.id, role_name)
        session.delete(role)
        session.commit()
    embed = generate_embed(
            title="Role removed",
            description="The role %s has been removed from the database." % role_name,  # noqa
            color=discord.Color.green())

    await ctx.interaction.response.send_message(embed=embed)


@discord.ext.commands.hybrid_command(
        name='list_battlepower_roles',
        help='List the roles to check the battlepower')
async def list_roles(ctx):
    # Get the discord server roles and list them
    # Usage example
    # /list_battlepower_roles
    with get_session() as session:
        roles = get_roles(session, ctx.guild.id)
        embed = generate_embed(
                title="Battlepower Roles",
                description="List of roles to be given when reaching a certain battlepower\n",
                color=discord.Color.blue())
        for role in roles:
            embed.description += f"**{role.role_name}** - "
            embed.description += f"{role.required_battlepower}\n"
        await ctx.interaction.response.send_message(embed=embed)


@discord.ext.commands.hybrid_command(
        name='update_battlepower_role',
        help='Update a rank to check the battlepower')
async def update_role(ctx, role_name, battlepower):
    # Get the discord server roles, search for the one with the prompt name
    # and update it in the db
    # Usage example
    # /update_battlepower_role "Role name" 1000
    dc_role = next(
            (role for role in ctx.guild.roles if role.name == role_name), None)
    if not dc_role:
        embed = generate_embed(
                title="Role not found",
                description="Role %s not found in the server" % role_name,
                color=discord.Color.red())
        await ctx.interaction.response.send_message(embed=embed)
        return

    with get_session() as session:
        role = get_or_create_role(
                session, ctx.guild.id, dc_role.id, role_name)
        role.required_battlepower = battlepower
        session.commit()
    embed = generate_embed(
            title="Role updated",
            description="The role %s has been updated in the database, it will be given when user reaches %s battlepower." % (  # noqa
                role_name, battlepower),
            color=discord.Color.green())

    await ctx.interaction.response.send_message(embed=embed)


def roles_command_setup(client):
    client.add_command(add_role)
    client.add_command(remove_role)
    client.add_command(list_roles)
    client.add_command(update_role)
