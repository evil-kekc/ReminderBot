from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

user_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .row('Добавить напоминание')

calendar = ReplyKeyboardMarkup(resize_keyboard=True)
calendar.row('Простой календарь')

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(KeyboardButton('Отмена'))
choice_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .row(KeyboardButton('Да'), KeyboardButton('Нет')).row(KeyboardButton('Отмена'))

url_inline_kb = InlineKeyboardMarkup(resize_keyboard=True) \
    .add(InlineKeyboardButton(text='Ссылка на гитхаб', url='https://github.com/evil-kekc/HerokuTest'))
