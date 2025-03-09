from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

role_inline_kb = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text="Учитель", callback_data="role_teacher"),
         InlineKeyboardButton(text="Родитель/Опекун", callback_data="role_parent"),
         InlineKeyboardButton(text="Иное", callback_data="role_other"),
         ],
    ]
)