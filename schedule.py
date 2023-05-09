import asyncio

import aioschedule

from bot_config import bot
from bot_config import reminder_bot_db


async def send_reminder():
    all_info = reminder_bot_db.send_remind()
    if all_info is not None:
        for remind in all_info:
            user_id = int(remind[0])
            name = remind[1]
            text = remind[2]

            await bot.send_message(user_id, f'{name}, напоминаю:\n\n{text}')


async def scheduler():
    aioschedule.every(1).minute.do(send_reminder)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
