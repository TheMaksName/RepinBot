from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

role_inline_kb = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text="Учитель", callback_data="role_teacher"),
         InlineKeyboardButton(text="Родитель/Опекун", callback_data="role_parent"),
         InlineKeyboardButton(text="Иное", callback_data="role_other"),
         ],
    ]
)

def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):

        keyboard = InlineKeyboardBuilder()

        for text, data in btns.items():
            keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
        return keyboard.adjust(*sizes).as_markup()
