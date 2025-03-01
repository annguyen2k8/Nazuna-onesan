from datetime import datetime
import pytz

import asyncio

import discord
from discord.ext import commands

class Status(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
        self.bot.loop.create_task(self.status_task())
    
    # region Bot.status_task
    # Usually online from about 8-9 pm until early morning (around 4-5 am).
    # A freat dracular roleplay
    async def status_task(self) -> None:
        tz = pytz.timezone('Asia/Tokyo')
        while not self.bot.is_closed():
            hour = datetime.now(tz=tz).hour
            status = discord.Status.online if hour >= 20 or hour <= 4 else discord.Status.idle
            await self.bot.change_presence(status=status)
            await asyncio.sleep(60)

async def setup(bot:commands.Bot):
    bot.add_cog(Status(bot))