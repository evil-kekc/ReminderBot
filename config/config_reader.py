import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    BOT_TOKEN: str
    HOST_URL: str
    MONGO_DB_URL: str
    ADMIN_ID: int
    DB: str
    TIME_DIRECTION: int


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    settings = config["BOT_CONFIG"]

    return Config(
        tg_bot=TgBot(
            BOT_TOKEN=settings["BOT_TOKEN"],
            HOST_URL=settings["HOST_URL"],
            MONGO_DB_URL=settings["MONGO_DB_URL"],
            ADMIN_ID=int(settings["ADMIN_ID"]),
            DB=settings["DB"],
            TIME_DIRECTION=int(settings["TIMEDELTA"]),
        )
    )
