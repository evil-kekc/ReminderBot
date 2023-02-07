import logging

import pymongo
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from config import load_config
from databases.mongo_db import MongoDB

storage = MemoryStorage()

logger = logging.getLogger(__name__)

config = load_config(r'config/config.ini')

client = pymongo.MongoClient(config.tg_bot.MONGO_DB_URL)
db = client.ReminderBot
collection = db.new_users

reminder_bot_db = MongoDB(collection)

TOKEN = config.tg_bot.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
