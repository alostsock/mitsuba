import argparse
import logging
import sys
from logging import FileHandler, StreamHandler

from .bot import Bot
from .config import read_config


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
        "--quiet",
        action="store_true",
        help="Suppress stdout",
    )
    return argparser.parse_args()


def setup_logging(log_level: int, quiet: bool):
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
        datefmt="[%Y/%m/%d %H:%M:%S]",
    )

    name = __package__
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    file_handler = FileHandler(f"{name}.log", encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(log_level)
    discord_file_handler = FileHandler("discord.log", encoding="utf-8", mode="w")
    discord_file_handler.setFormatter(formatter)
    discord_logger.addHandler(discord_file_handler)

    if not quiet:
        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
        discord_logger.addHandler(stdout_handler)

    return logger


if __name__ == "__main__":
    args = parse_args()

    log_level = getattr(logging, args.log_level)
    logger = setup_logging(log_level=log_level, quiet=args.quiet)

    logger.info("Starting bot...")

    config = read_config(args.config)
    bot = Bot(config)
    bot.run()
