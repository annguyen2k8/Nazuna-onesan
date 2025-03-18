import discord
from discord import app_commands
from discord.ext import commands

from discord.utils import *

from utils.formating import *

from base import BotBase

class Events(commands.Cog):
    def __init__(self, bot:BotBase) -> None:
        self.bot = bot

async def setup(bot:BotBase) -> None:
    await bot.add_cog(Events(bot))