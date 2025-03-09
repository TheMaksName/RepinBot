from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command


from sqlalchemy.ext.asyncio import AsyncSession

from FSM.FSM_user_private import RegistrationUser, MainStates
from common.validation import validate_fio, validate_phone_number
from database.orm_query import orm_AddActiveUser, orm_AddUser, orm_Change_RegStaus, orm_Check_avail_user, \
    orm_Get_info_user
from kbds import reply
from kbds.inline import role_inline_kb

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    try:
        user_name = await orm_Check_avail_user(session, message.from_user.id)
        print(user_name)
        if not user_name:
            info_user = dict()
            info_user['user_id'] = message.from_user.id
            info_user['nickname'] = message.from_user.username or 'не установлен'
            await orm_AddUser(session, info_user)
            await state.set_state(MainStates.before_registration)
            await message.answer("Здесь должен быть приветственный текст. Появится позже...",
                                 reply_markup=reply.start_kb)
        else:
            await state.set_state(MainStates.after_registration)
            await message.answer(f"Привет {user_name.split(" ")[1]}, давно не виделись", reply_markup=reply.menu_kb)
    except Exception as e:
        await message.answer("Извените, что-то пошло не так. Попробуйте позже")

@user_private_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer("Открываю меню...", reply_markup=reply.menu_kb)

@user_private_router.message(F.text.lower() == 'новости')
async def news(message: Message):
    await message.answer("Новостей пока нет(((")

@user_private_router.message(MainStates.after_registration, F.text.lower() == 'мой профиль')
async def news(message: Message, session: AsyncSession):
    data = await orm_Get_info_user(session, message.from_user.id)
    await message.answer("Открываю Ваш профиль",)
    result_answer = f"""
                ФИО: {data.name}
                Школа: {data.school}
                Номер телефона: {data.phone_number}
                электронная почта: {data.email}
                ФИО наставника: {data.name_mentor}
                {"Должность наставника: " + data.post_mentor if data.post_mentor else ''}"""

    await message.answer(result_answer)

@user_private_router.message(MainStates.before_registration)
async def process_action(message: Message, state: FSMContext):
    if message.text.lower() == 'зарегистрироваться':
        await message.answer("Отлично, давай регистрироваться)))", reply_markup=reply.del_kbd)
        await message.answer('Введите Ваше ФИО в формате (Фамилия Имя Отчество)')
        await state.set_state(RegistrationUser.name_user)




#Код ниже для машины состояний (FSM) для регистрации участника
@user_private_router.message(RegistrationUser.name_user)
async def register_step_name(message: Message, state: FSMContext):
    if validate_fio(message.text.strip()):
        await message.answer('Введите полное название вашей школы')
        await state.update_data(name_user=message.text)
        await state.set_state(RegistrationUser.school)
    else:
        await message.answer("Пожалуйста, введи ФИО в правильном формате (Фамилия Имя Отчество).")

@user_private_router.message(RegistrationUser.school)
async def register_step_phone_number(message: Message, state: FSMContext):

    await state.update_data(school=message.text)
    await message.answer('Введите номер Вашего телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')
    await state.set_state(RegistrationUser.phone_number)


@user_private_router.message(RegistrationUser.phone_number, F.text)
async def register_step_email(message: Message, state: FSMContext):
    phone_number = message.text
    if validate_phone_number(phone_number):
        await state.update_data(phone_number=message.text)
        await message.answer('Введите адрес Вашей электронной почты')
        await state.set_state(RegistrationUser.mail)
    else:
        await message.answer("Пожалуйста, введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.")


@user_private_router.message(RegistrationUser.mail, F.text)
async def register_step_name_mentor(message: Message, state: FSMContext):

    # Валидация почты

    await state.update_data(email=message.text)
    await message.answer('Введите полное ФИО Вашего наставника в формате (Фамилия Имя Отчество)')
    await state.set_state(RegistrationUser.name_mentor)


@user_private_router.message(RegistrationUser.name_mentor, F.text)
async def register_step_status_mentor(message: Message, state: FSMContext):
    name_mentor = message.text
    if validate_fio(name_mentor):
        await state.update_data(name_mentor=message.text)
        await message.answer(
            'Выберите роль вашего наставника.',
        reply_markup=role_inline_kb)
        await state.set_state(RegistrationUser.status_mentor)
    else:
        await message.answer("Пожалуйста, введи ФИО в правильном формате (Фамилия Имя Отчество).")

@user_private_router.message(RegistrationUser.input_status_mentor)
async def register_input_status_mentor(message: Message, state: FSMContext, session:AsyncSession):
    await state.update_data(post_mentor=message.text)
    await register_step_finish(message=message, state=state, session=session)

@user_private_router.message(RegistrationUser.post_mentor)
async def register_input_post_mentor(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(post_mentor=message.text)
    await register_step_finish(message=message, state=state, session=session)

# @user_private_router.message(AddUser.input_status_mentor)
# @user_private_router.message(AddUser.post_mentor)
async def register_step_finish(message: Message, state: FSMContext, session: AsyncSession, user_id: int = None):
    data = await state.get_data()

    try:
        await orm_AddActiveUser(session, data)

        if user_id:
            await state.update_data(user_id=user_id)
            await orm_Change_RegStaus(session, user_id, True)
        else:
            await state.update_data(user_id=message.from_user.id)
        await message.answer('Регистрация успешно пройдена.')

        result_answer = f"""
            ФИО: {data['name_user']}
            Школа: {data['school']}
            Номер телефона: {data['phone_number']}
            электронная почта: {data['mail']}
            ФИО наставника: {data['name_mentor']}
            {"Должность наставника: " + data['post_mentor'] if data['post_mentor'] else ''}"""

        await message.answer(result_answer)
        await message.answer('Открываю меню...', reply_markup=reply.menu_kb)
        await state.set_state(MainStates.after_registration)
    except Exception as e:
        await message.answer("Что-то пошло не так... Попробуйте позже")
        await state.clear()


#Обработка Инлайн при регистрации пользователя
@user_private_router.callback_query(RegistrationUser.status_mentor)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext, session:AsyncSession):
    role = callback_query.data.split('_')[1]
    await callback_query.answer()
    if role == 'teacher':
        await callback_query.message.answer('Введите должность вашего наставника.')
        await state.set_state(RegistrationUser.post_mentor)
    elif role == 'other':
        await callback_query.message.answer('Введите роль вашего наставника.')
        await state.set_state(RegistrationUser.input_status_mentor)
    else:
        await state.update_data(post_mentor='Родитель/опекун')
        await register_step_finish(message=callback_query.message, state=state, session=session, user_id=callback_query.from_user.id)


