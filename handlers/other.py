import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from buttons import url_inline_kb, user_kb
from config import bot


async def send_url(message: types.Message, state=FSMContext):
    await bot.send_message(message.from_user.id, 'Код бота можете посмотреть на GitHub',
                           reply_markup=url_inline_kb)


async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Ввод отменен', reply_markup=user_kb)


def other_register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, state="*", commands=['отмена', 'cancel'])
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True), state="*")

    dp.register_message_handler(send_url, commands='get_code')
