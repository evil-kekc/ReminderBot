import asyncio
import logging

from aiogram import types, Dispatcher, Bot
from aiogram.types import BotCommand
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status

from bot_config import dp, bot, TOKEN, logger, config
from bot_config import reminder_bot_db
from handlers import bug_report, reminder, other
from schedule import scheduler

app = FastAPI()
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = config.tg_bot.HOST_URL + WEBHOOK_PATH


async def set_commands(bot_: Bot):
    """Set commands for bot

    :param bot_: Bot class instance
    :return:
    """
    commands = [
        BotCommand(command='/start', description='Начало работы'),
        BotCommand(command='/cancel', description='Отмена'),
        BotCommand(command='/get_code', description='Исходный код бота'),
        BotCommand(command='/bug_report', description='Отправить сообщение об ошибке'),
    ]

    await bot_.set_my_commands(commands)


async def bot_main():
    """Applies all bot settings

    :return:
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger.info('Starting bot')

    bug_report(dp)
    other(dp)
    reminder(dp)

    await set_commands(bot)


@app.on_event("startup")
async def on_startup():
    """Setting up a webhook

    :return:
    """
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )
    asyncio.create_task(scheduler())


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Getting Telegram updates

    :param update: Telegram update
    :return:
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await bot_main()
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    """Closing session and delete webhook

    :return:
    """
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
            status_code=status.HTTP_201_CREATED,
            media_type='application/json'
        )
    else:
        return JSONResponse(
            content=response[2],
            status_code=status.HTTP_404_NOT_FOUND,
            media_type='application/json'
        )
