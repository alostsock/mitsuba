import logging

import discord
from discord.ext import commands

from .config import Config
from .database import Database
from .models import Guild

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, config: Config) -> None:
        self.config = config

        self.db = Database(config.db_url)

        intents = discord.Intents(
            guilds=True,
            members=True,
            message_content=True,
        )

        super().__init__(command_prefix=config.command_prefix, intents=intents)

    def run(self):
        super().run(token=self.config.token, log_handler=None)

    async def on_ready(self):
        logger.info(f"Ready! Connected to {len(self.guilds)} guilds")

    async def on_guild_available(self, guild: discord.Guild):
        if guild.id in self.config.guild_ids:
            await self.db.upsert([Guild(guild.id)])
