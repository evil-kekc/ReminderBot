import logging
import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from buttons import cancel_kb
from config import bot


class Report(StatesGroup):
    send_report = State()


async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())


async def start_mess(message: types.Message):
    await bot.send_message(message.from_user.id, f'Опишите проблему, с которой вы столкнулись', reply_markup=cancel_kb)
    await Report.send_report.set()


async def choice(message: types.Message, state=FSMContext):
    await bot.send_message(os.getenv('ADMIN_ID'), message.text)
    await message.reply('Спасибо за ваш отчет, мы рассмотрим ваше обращение в ближайшее время',
                        reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def bug_report_register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, state="*", commands=['отмена', 'cancel'])
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True), state="*")

    dp.register_message_handler(start_mess, commands='bug_report')

    dp.register_message_handler(choice, state=Report.send_report)
