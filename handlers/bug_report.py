import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from bot_config import bot, config
from buttons import cancel_kb


class ReportAnswer(StatesGroup):
    send_answer = State()


class Report(StatesGroup):
    send_report = State()


call_back_info = CallbackData('report_answer', 'user_id')


async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())


async def start_mess(message: types.Message):
    await bot.send_message(message.from_user.id, f'Опишите проблему, с которой вы столкнулись', reply_markup=cancel_kb)
    await Report.send_report.set()


async def choice(message: types.Message, state: FSMContext):
    send_report_answer = InlineKeyboardMarkup(resize_keyboard=True).add(
        InlineKeyboardButton(text='Ответить', callback_data=call_back_info.new(user_id=message.from_user.id)))

    await bot.copy_message(config.tg_bot.ADMIN_ID, message.from_user.id, message.message_id,
                           reply_markup=send_report_answer)

    await message.reply('Спасибо за ваш отчет, мы рассмотрим ваше обращение в ближайшее время',
                        reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def get_answer(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_data['user_id']

    await state.update_data(id=user_id)
    await state.update_data(message_id=callback_query.message.message_id)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'Введите текст ответа')

    await state.set_state(ReportAnswer.send_answer.state)


async def send_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['id']
    message_id = data['message_id']
    await bot.delete_message(message.from_user.id, message_id)
    await bot.send_message(user_id, message.text)
    await state.finish()


def bug_report_register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, state="*", commands=['отмена', 'cancel'])
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True), state="*")

    dp.register_message_handler(start_mess, commands='bug_report')

    dp.register_message_handler(choice, state=Report.send_report)

    dp.register_message_handler(send_answer, state=ReportAnswer.send_answer)

    dp.register_callback_query_handler(get_answer, call_back_info.filter())
