import os

import pymongo
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from db import MongoDB

storage = MemoryStorage()

client = pymongo.MongoClient(os.getenv('MONGO_DB_URL'))
db = client.test_bot_db
collection = db.new_users

reminder_bot_db = MongoDB(collection)

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
