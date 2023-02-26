import logging

import discord
from discord.ext import commands

from .config import Config

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, config: Config) -> None:
        self.config = config

        intents = discord.Intents.none()
        intents.guilds = True
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix=config.command_prefix, intents=intents)

    def run(self):
        super().run(token=self.config.token, log_handler=None)

    async def on_ready(self):
        logger.info(f"Ready! Connected to {len(self.guilds)} guilds")
