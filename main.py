import os

import discord
from discord import ApplicationContext
from discord.utils import get
from dotenv import load_dotenv

from commands.day import Day
from commands.end import End
from commands.killplayer import KillPlayer
from commands.mafia import Mafia
from commands.night import Night
from commands.start import Start
from config import GUILD_ID
from discordroles import DiscordRoles
from game import Type

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = discord.Bot(intents=discord.Intents.all())


@bot.slash_command(name="start", description="Начать игру", guild_ids=[GUILD_ID])
async def start(ctx: ApplicationContext,
                type: discord.Option(str, required=True, choices=["Городская", "Классическая"])):
    if type == "Городская":
        t = Type.CITY
    else:
        t = Type.CLASSIC

    await Start.start(ctx, t)


@bot.slash_command(name="setdon", description="Назначить дона мафии", guild_ids=[GUILD_ID])
async def set_don(ctx: ApplicationContext, member: discord.Option(discord.SlashCommandOptionType.user, required=True)):
    await Mafia.set_don(ctx, member)


@bot.slash_command(name="night", description="Начать ночь", guild_ids=[GUILD_ID])
async def night(ctx: ApplicationContext):
    await Night.night(ctx)


@bot.slash_command(name="day", description="Начать день", guild_ids=[GUILD_ID])
async def day(ctx: ApplicationContext):
    await Day.day(ctx)


@bot.slash_command(name="killplayer", description="Начать день", guild_ids=[GUILD_ID])
async def kill_player(ctx: ApplicationContext, member: discord.Option(discord.SlashCommandOptionType.user, required=True)):
    await KillPlayer.kill_player(ctx, member)


@bot.slash_command(name="end", description="Закончить игру", guild_ids=[GUILD_ID])
async def end(ctx: ApplicationContext):
    await End.end(ctx)


@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)

    for r in DiscordRoles.values():
        if not get(guild.roles, name=r):
            await guild.create_role(name=r)
            print(f"Создание роли {r}")


bot.run(TOKEN)
