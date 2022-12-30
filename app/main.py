import asyncio
import os

from aiogram import types, Dispatcher, Bot
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status

from bot_config import dp, bot, TOKEN
from bot_config import reminder_bot_db
from handlers import bug_report, reminder, other
from schedule import scheduler

app = FastAPI()
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = os.getenv('HOST_URL') + WEBHOOK_PATH


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
    asyncio.create_task(scheduler())


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Setting up a webhook

    :param update: Telegram update
    :return:
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    bug_report(dp)
    reminder(dp)
    other(dp)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    await bot.delete_webhook()


@app.get('/')
async def home_page():
    """GET request to getting info about bot running

    :return: info about bot running
    """
    return 'Bot running successfully!'


@app.get(f'{WEBHOOK_PATH}/info')
async def info():
    """GET request to getting all info from DB

    :return: JSON Response
    """
    response = reminder_bot_db.get_all_values_json()

    if response[1] == status.HTTP_200_OK:
        return JSONResponse(
            content=response[0],
            status_code=status.HTTP_200_OK,
            media_type='application/json'
        )
    else:
        return JSONResponse(
            content=response[0],
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )


@app.get(f'{WEBHOOK_PATH}/clear')
async def clear_db():
    """GET request to clear the DB

    :return: JSON Response
    """
    response = reminder_bot_db.delete_all_values()
    if response[1] == status.HTTP_200_OK:
        return JSONResponse(
            content=response[0],
            status_code=status.HTTP_200_OK,
            media_type='application/json'
        )
    else:
        return JSONResponse(
            content=response[0],
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )


@app.post(f'{WEBHOOK_PATH}/post/')
async def add_remind(remind: dict):
    """POST request to adding a reminder into DB

    :return: JSON Response
    """
    user_id = remind['user_id']
    name = remind['name']
    date = remind['date']
    text = remind['text']

    response = reminder_bot_db.insert_one_value(user_id, name, date, text)
    if response[1] == status.HTTP_200_OK:
        return JSONResponse(
            content=response[2],
            status_code=status.HTTP_200_OK,
            media_type='application/json'
        )
    else:
        return JSONResponse(
            content=response[2],
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )
