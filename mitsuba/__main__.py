import argparse
import logging
import sys
from logging import FileHandler, StreamHandler

import discord

from .bot import Bot
from .config import read_config

discord.VoiceClient.warn_nacl = False


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--config",
        default="config.json",
        help="Specify a configuration file",
    )
    argparser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level",
    )
    argparser.add_argument(
        "--log-discord",
        action="store_true",
        help="Include discord.py output in logs",
    )
    argparser.add_argument(
        "--log-sql",
        action="store_true",
        help="Include SQL output in logs",
    )
    argparser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout",
    )
    return argparser.parse_args()


def setup_logging(log_level: int, log_discord: bool, log_sql: bool, use_stdout: bool):
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="[%Y/%m/%d %H:%M:%S]",
    )

    file_handler = FileHandler(f"{__package__}.log", encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter)

    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    for name, level, enabled in [
        (__package__, log_level, True),
        ("discord", logging.INFO, log_discord),
        ("sqlalchemy.engine", logging.INFO, log_sql),
    ]:
        if enabled:
            logger = logging.getLogger(name)
            logger.setLevel(level)
            logger.addHandler(file_handler)
            if use_stdout:
                logger.addHandler(stdout_handler)


if __name__ == "__main__":
    args = parse_args()

    setup_logging(
        log_level=getattr(logging, args.log_level),
        log_discord=args.log_discord,
        log_sql=args.log_sql,
        use_stdout=not args.quiet,
    )

    logger = logging.getLogger(__package__)
    logger.info("Starting bot...")

    config = read_config(args.config)
    bot = Bot(config)
    bot.run()
