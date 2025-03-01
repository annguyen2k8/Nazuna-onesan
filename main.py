import os
import sys
import json
import pathlib
import asyncio
import warnings
import datetime
import traceback

from datetime import datetime
import pytz

from typing import *

import logging
import logging.handlers
from logging import Logger

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from utils.formating import *

# Uncomment if you want to use mobile status for your bot
# from utils.mobile import *

class Bot(commands.Bot):
    # region Bot.__init__
    def __init__(self, config:Dict) -> None:
        intents = discord.Intents.all()
        
        self.start_time = datetime.now()
        
        super().__init__(
            command_prefix=config.pop('command_prefix', ['!', '?']),
            description=config.pop('description', None),
            intents=intents
        )
        self.config = config
        self.logger = set_logger(self)
        
        self.tz = pytz.timezone('Asia/Tokyo')
    
    # region Bot.setup_hook
    async def setup_hook(self) -> None:
        self.loop.create_task(self.load_cogs())     

    # region Bot.load_cogs
    async def load_cogs(self) -> None:
        """
        Loads all cogs in folder.
        """
        await self.wait_until_ready()
        await asyncio.sleep(0.1)
        loaded_cogs = []
        failed_cogs = []
        cogs_directory = pathlib.Path('./cogs')
        for cog in cogs_directory.iterdir():
            cog_name = cog.name
            amtemp = 0
            while amtemp < 3:
                try:
                    await self.load_extension(f'cogs.{cog_name}.main')
                    loaded_cogs.append(cog_name)
                    self.logger.info(f"Loaded {cog_name}'s cog")
                    break
                except Exception as e:
                    self.logger.error(f"Error to load {cog_name} cog")
                    failed_cogs.append(cog_name)
                    self.logger.exception(e)
                    await asyncio.sleep(5)
                    amtemp += 1
        await self.sync_commands()
    
    # region Bot.sync_commands
    async def sync_commands(self) -> None:
        try:
            sync = await self.tree.sync()
            self.logger.info(f"Total {len(sync)} slash commands, {len(self.commands)} normal commands")
        except Exception as error:
            self.logger.error(error)
    
    # region Bot.on_ready
    async def on_ready(self) -> None:
        now = datetime.now()
        elapsed_time = now - self.start_time
        self.logger.info(f"Logged bot's {self.user} (ID: {self.application.id})")
        self.logger.info(f"Took {round(elapsed_time.total_seconds()*1000)}ms to start")
        self.status_task.start()

    # region Bot.on_command_error
    async def on_command_error(self, ctx:commands.Context, error:commands.errors.CommandError):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("You don't have permission to use this command")
        self.logger.error("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        
        # owner = self.application.owner
        # channel = await owner.create_dm()
        # await channel.send(
        #     f"{box(traceback.format_exc())}\n" + \
        #     f"User: {ctx.author}\n" + \
        #     f"Content: {ctx.message.content}\n" + \
        #     f"Args: {error.args}"
        #     )
    
    # region Bot.status_task
    # Usually online from about 8-9 pm until early morning (around 4-5 am).
    # A freat dracular roleplay
    @tasks.loop(minutes=5)
    async def status_task(self) -> None:
        hour = datetime.now(tz=self.tz).hour
        status = discord.Status.online if hour >= 20 or hour <= 4 else discord.Status.idle
        if self.status != status:
            await self.change_presence(status=status)

# region set_logger
def set_logger(bot:commands.Bot) -> Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    while logger.hasHandlers():    logger.setLevel(logging.INFO)


    log_format = logging.Formatter(
        '{asctime} {levelname:<8} {module}.{funcName} '
        '{message}',
        datefmt="[%Y-%m-%d %H:%M:%S]",
        style='{'
        )
    
    dpy_handler = logging.StreamHandler()
    dpy_handler.setFormatter(log_format)
    logger.addHandler(dpy_handler)
    
    os.makedirs('logs', exist_ok=True)
    fhandler = logging.handlers.RotatingFileHandler(
        filename=f'logs/{bot.start_time.strftime("%Y-%m-%d")}.log',
        maxBytes=10**7,
        backupCount=5
        )
    fhandler.setFormatter(log_format)
    logger.addHandler(fhandler)

    return logger

# region start_bot
def start_bot(config) -> None:
    bot = Bot(config)
    bot.run(config.pop('token'), log_handler=None)

if __name__ == '__main__':
    # Filter warnings
    warnings.filterwarnings('ignore')
    
    # Avoid event loop error on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Load config and start bot
    config = json.loads(open('config.json').read())
    start_bot(config)