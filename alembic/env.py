import asyncio
import logging
import sys
from logging import FileHandler, StreamHandler

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

import mitsuba
from alembic import context

# Provides access to the values within alembic.ini
config = context.config

# Setup loggers
formatter = logging.Formatter(
    fmt="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
    datefmt="[%Y/%m/%d %H:%M:%S]",
)
file_handler = FileHandler(f"alembic.log", encoding="utf-8", mode="w")
file_handler.setFormatter(formatter)
stdout_handler = StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
for name, level in [
    ("alembic", logging.INFO),
    ("sqlalchemy.engine", logging.WARN),
]:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

# Used for auto-generating migrations with `alembic revision --autogenerate`
# See https://alembic.sqlalchemy.org/en/latest/autogenerate.html
target_metadata = mitsuba.models.Base.metadata

# Read in the connection URL from the config file the bot uses.
# This is configured by mitsuba.config in alembic.ini
mitsuba_config_file = config.get_main_option("mitsuba.config")
assert mitsuba_config_file is not None
mitsuba_config = mitsuba.config.read_config(mitsuba_config_file)
url = mitsuba_config.db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
