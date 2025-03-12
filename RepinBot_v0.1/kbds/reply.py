from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
        KeyboardButton(text="Зарегистрироваться"),
        KeyboardButton(text="Выйти"),
        ],

    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?'

)

menu_kb = ReplyKeyboardMarkup (
    keyboard=[
        [
            KeyboardButton(text="Новости"),
            KeyboardButton(text="Мой профиль")
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?'
)

del_kbd = ReplyKeyboardRemove()

