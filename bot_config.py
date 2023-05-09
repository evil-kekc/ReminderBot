import logging
import os
import sys
from pathlib import Path

import pymongo
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from config import load_config

storage = MemoryStorage()

logger = logging.getLogger(__name__)

BASE_DIR = Path(os.path.abspath(__file__)).parent.__str__()

config = load_config(fr'{BASE_DIR}/config/config.ini')

if config.tg_bot.DB == 'MONGO_DB':
    from databases.mongo_db import MongoDB

    client = pymongo.MongoClient(config.tg_bot.MONGO_DB_URL)
    db = client.ReminderBot
    collection = db.new_users

    reminder_bot_db = MongoDB(collection)

elif config.tg_bot.DB == 'SQLite_DB':
    from databases.sqlite_db import SQLiteDB
    reminder_bot_db = SQLiteDB()

else:
    logging.error('No database selected')
    sys.exit()

client = pymongo.MongoClient(config.tg_bot.MONGO_DB_URL)
db = client.ReminderBot
collection = db.new_users

TOKEN = config.tg_bot.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
