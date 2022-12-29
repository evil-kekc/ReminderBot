import logging
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from buttons import user_kb, cancel_kb, choice_kb
from calendars import SimpleCalendar, simple_calendar_callback
from config import bot
from config import reminder_bot_db


class FSMAdmin(StatesGroup):
    send_info = State()
    get_date = State()
    get_text = State()
    confirmation = State()
    finish = State()


async def start_mess(message: types.Message):
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}, я бот, который может '
                                                 f'напомнить тебе о важных мероприятиях',
                           reply_markup=user_kb)


async def send_calendar(message: types.Message, state=FSMContext):
    await message.answer(f'Выбери дату напоминания', reply_markup=await SimpleCalendar().start_calendar())
    await message.answer('Для отмены, нажмите отмена внизу экрана', reply_markup=cancel_kb)
    await state.set_state(FSMAdmin.send_info.state)


async def send_question(callback_query: CallbackQuery, callback_data: CallbackData, state=FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    now_date = datetime.now().date()

    user_date = datetime.strptime(f'{date}', '%Y-%m-%d %H:%M:%S').date()

    if now_date > user_date:
        await bot.send_message(callback_query.from_user.id, 'Ошибка ввода. Введенная дата уже прошла',
                               reply_markup=user_kb)
        return

    if selected:
        async with state.proxy() as data:
            data['date'] = date.strftime("%d.%m.%Y")

        await bot.send_message(callback_query.from_user.id, f'Введите время напоминания в '
                                                            'формате <b>ЧЧ:MM</b> \nНапример: <b>08:58</b>',
                               parse_mode=types.ParseMode.HTML, reply_markup=cancel_kb)
        await state.set_state(FSMAdmin.get_date.state)
    else:
        return


async def get_info(message: types.Message, state=FSMContext):
    try:
        if message.text == 'Отмена':
            await state.finish()
            await message.reply('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())
        else:
            info = await state.get_data()
            date = info.get('date')
            all_date = f'{message.text} - {date}'

            now_date = datetime.now()

            user_date = datetime.strptime(f'{all_date}', '%H:%M - %d.%m.%Y')

            if now_date >= user_date:
                await message.answer('Ошибка ввода. Введенная дата уже прошла', reply_markup=user_kb)
                await state.finish()
            else:
                async with state.proxy() as data:
                    data['all_date'] = all_date

                await bot.send_message(message.from_user.id, 'Введите текст напоминания', reply_markup=cancel_kb)
                await FSMAdmin.get_text.set()
    except ValueError:
        await bot.send_message(message.from_user.id,
                               'Неправильный формат даты\n'
                               'Проверьте правильность введенных данных и введите время снова',
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=cancel_kb)
        await FSMAdmin.get_date.set()


async def get_text(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    data = await state.get_data()
    date = data.get('all_date')
    text = data.get('text')

    await bot.send_message(message.from_user.id, f'Проверьте правильность введенных данных:\n'
                                                 f'{date}\n{text}', reply_markup=choice_kb)
    await FSMAdmin.finish.set()


async def save_info(message: types.Message, state=FSMContext):
    data = await state.get_data()
    date = data.get('all_date')
    text = data.get('text')

    user_id = message.from_user.id
    name = message.from_user.first_name

    if message.text == 'Да':
        if reminder_bot_db.insert_one_value(user_id, name, date, text)[0]:
            await message.answer('Ваши данные сохранены', reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
        else:
            await message.answer('Ваши данные не сохранены, возможно, они уже добавлены',
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
    elif message.text == 'Нет':
        await state.finish()
        await message.reply('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())


def reminder_register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_mess, commands=['start'])

    dp.register_callback_query_handler(send_question, simple_calendar_callback.filter(), state=FSMAdmin.send_info)

    dp.register_message_handler(get_info, state=FSMAdmin.get_date)

    dp.register_message_handler(send_calendar, Text(equals='Добавить напоминание', ignore_case=True),
                                state='*')

    dp.register_message_handler(get_text, state=FSMAdmin.get_text)

    dp.register_message_handler(save_info, state=FSMAdmin.finish)
