from discord import ApplicationContext, Member
from discord.utils import get

import game
from discordroles import DiscordRoles


def get_role(ctx: ApplicationContext, role: DiscordRoles):
    return get(ctx.guild.roles, name=role.value)


async def check_permission(ctx: ApplicationContext):
    if get_role(ctx, DiscordRoles.HOST) not in ctx.user.roles:
        await ctx.respond("Нет прав", ephemeral=True)
        return True


async def check_game(ctx: ApplicationContext):
    if game.HOST is None:
        await ctx.respond("Сейчас нет активной игры", ephemeral=True)
        return True


def get_player_by_role(role):
    for p in game.players:
        if p.role == role:
            return p

    return None


def get_players_by_role(role):
    players = [p for p in game.players if p.role == role]

    return players


def get_player_by_member(member: Member):
    for p in game.players:
        if p.member.id == member.id:
            return p

    return None


def get_player_by_id(user_id: int):
    for p in game.players:
        if p.member.id == user_id:
            return p

    return None
