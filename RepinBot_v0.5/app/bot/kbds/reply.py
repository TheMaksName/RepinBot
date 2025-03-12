from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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

def get_keyboard(
        *btns: str,
        placeholder: str = None,
        sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()

    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)


del_kbd = ReplyKeyboardRemove()



