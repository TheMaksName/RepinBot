from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from aiogram.filters import Command


from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.FSM.FSM_user_private import RegistrationUser, User_MainStates
from app.bot.handlers.user_edit_profile import user_view_profile_router
from app.bot.handlers.user_registartion import user_registration_router
from app.kbds.reply import get_keyboard
from app.database.orm_query import orm_AddUser, \
    orm_Get_info_user, orm_Check_register_user, orm_Check_avail_user, orm_get_news
from app.kbds import reply

user_private_router = Router()
user_private_router.include_router(user_registration_router)
user_private_router.include_router(user_view_profile_router)


@user_private_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer("Открываю меню...", reply_markup=reply.menu_kb)

@user_private_router.message(F.text.lower() == 'новости')
async def news(message: Message, session: AsyncSession):
    all_news = await orm_get_news(session)
    if all_news:
        for news in all_news:
            await message.answer_photo(
                news.image,
                caption=f'<strong>{news.title}</strong>\n{news.description}',
                parse_mode='HTML'
            )
        await message.answer("Вот последние новости:")
    else:
        await message.answer("Новостей пока нет(((")

@user_private_router.message(User_MainStates.after_registration, F.text.lower() == 'мой профиль')
async def get_user_profile(message: Message, session: AsyncSession, state: FSMContext):
    await state.set_state(User_MainStates.user_view_profile)
    data = await orm_Get_info_user(session, message.from_user.id)
    await message.answer("Открываю Ваш профиль",)
    result_answer = f"""
                ФИО: {data.name}
                Школа: {data.school}
                Номер телефона: {data.phone_number}
                электронная почта: {data.mail}
                ФИО наставника: {data.name_mentor}
                {"Должность наставника: " + data.post_mentor if data.post_mentor else ''}"""
    reply_markup=get_keyboard(
        "Редактировать",
        "Назад",
        placeholder="Выберите действие",
        sizes=(2,),
        )

    await message.answer(result_answer, reply_markup=reply_markup)



@user_private_router.message(User_MainStates.before_registration)
async def process_action(message: Message, state: FSMContext):
    if message.text.lower() == 'зарегистрироваться':
        await message.answer("Отлично, давай регистрироваться)))", reply_markup=reply.del_kbd)
        await message.answer('Введите Ваше ФИО в формате (Фамилия Имя Отчество)')
        await state.set_state(RegistrationUser.name_user)







