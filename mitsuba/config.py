import json
from typing import List, NamedTuple

from schema import And, Schema


class Config(NamedTuple):
    token: str
    command_prefix: str
    db_url: str
    guild_ids: List[str]


def read_config(filename: str) -> Config:
    schema = Schema(
        {
            "token": And(str, len),
            "command_prefix": And(str, lambda s: len(s) == 1),
            "db_url": And(str, len),
            "guild_ids": [int],
        }
    )

    with open(filename) as fh:
        config = json.load(fh)

    schema.validate(config)

    return Config(
        token=config["token"],
        command_prefix=config["command_prefix"],
        db_url=config["db_url"],
        guild_ids=config["guild_ids"],
    )
