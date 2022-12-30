import asyncio

import aioschedule

import config
from config import reminder_bot_db


async def send_reminder():
    """Send reminder

    :return:
    """
    if reminder_bot_db.send_remind():
        all_info = reminder_bot_db.send_remind()
        user_id = all_info[0]
        name = all_info[1]
        text = all_info[2]

        await config.bot.send_message(user_id, f'{name}, напоминаю:\n\n{text}')


async def scheduler():
    aioschedule.every(1).minute.do(send_reminder)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
