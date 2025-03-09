from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command

from sqlalchemy.ext.asyncio import AsyncSession

from common.validation import validate_fio, validate_phone_number
from database.models import ActiveUser
from database.orm_query import orm_AddActiveUser
from kbds import reply
from kbds.inline import role_inline_kb

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Здесь должен быть приветственный текст. Появится позже...", reply_markup=reply.start_kb)
    await state.clear()

@user_private_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer("Открываю меню...", reply_markup=reply.menu_kb)

@user_private_router.message(F.text.lower() == 'новости')
async def news(message: Message):
    await message.answer("Новостей пока нет(((", reply_markup=reply.menu_kb)

@user_private_router.message(F.text.lower() == 'мой профиль')
async def news(message: Message):
    await message.answer("Мой профиль", reply_markup=reply.menu_kb)



#Код ниже для машины состояний (FSM) для регистрации участника
class AddUser(StatesGroup):
    name_user = State()
    school = State()
    phone_number = State()
    mail = State()
    name_mentor = State()
    status_mentor = State()
    post_mentor = State()
    input_status_mentor = State()


@user_private_router.message(StateFilter(None),F.text.lower() == "зарегистрироваться")
async def register_step_name(message: Message, state: FSMContext):
    await message.answer('Введите Ваше ФИО в формате (Фамилия Имя Отчество)', reply_markup=reply.del_kbd)
    await state.set_state(AddUser.name_user)

@user_private_router.message(AddUser.name_user, F.text)
async def register_step_school(message: Message, state: FSMContext):
    if validate_fio(message.text.strip()):
        await message.answer('Введите полное название вашей школы')
        await state.update_data(name_user=message.text)
        await state.set_state(AddUser.school)
    else:
        await message.answer("Пожалуйста, введи ФИО в правильном формате (Фамилия Имя Отчество).")


@user_private_router.message(AddUser.school, F.text)
async def register_step_phone_number(message: Message, state: FSMContext):

    # Валидация школы

    await state.update_data(school=message.text)
    await message.answer('Введите номер Вашего телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')
    await state.set_state(AddUser.phone_number)


@user_private_router.message(AddUser.phone_number, F.text)
async def register_step_email(message: Message, state: FSMContext):
    phone_number = message.text
    if validate_phone_number(phone_number):
        await state.update_data(phone_number=message.text)
        await message.answer('Введите адрес Вашей электронной почты')
        await state.set_state(AddUser.mail)
    else:
        await message.answer("Пожалуйста, введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.")




@user_private_router.message(AddUser.mail, F.text)
async def register_step_name_mentor(message: Message, state: FSMContext):

    # Валидация почты

    await state.update_data(email=message.text)
    await message.answer('Введите полное ФИО Вашего наставника в формате (Фамилия Имя Отчество)')
    await state.set_state(AddUser.name_mentor)


@user_private_router.message(AddUser.name_mentor, F.text)
async def register_step_status_mentor(message: Message, state: FSMContext):
    name_mentor = message.text
    if validate_fio(name_mentor):
        await state.update_data(name_mentor=message.text)
        await message.answer(
            'Выберите роль вашего наставника.',
        reply_markup=role_inline_kb)
        await state.set_state(AddUser.status_mentor)
    else:
        await message.answer("Пожалуйста, введи ФИО в правильном формате (Фамилия Имя Отчество).")

@user_private_router.message(AddUser.input_status_mentor)
async def register_input_status_mentor(message: Message, state: FSMContext, session:AsyncSession):
    await state.update_data(post_mentor=message.text)
    await register_step_finish(message=message, state=state, session=session)

@user_private_router.message(AddUser.post_mentor)
async def register_input_post_mentor(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(post_mentor=message.text)
    await register_step_finish(message=message, state=state, session=session)

# @user_private_router.message(AddUser.input_status_mentor)
# @user_private_router.message(AddUser.post_mentor)
async def register_step_finish(message: Message, state: FSMContext, session: AsyncSession):

    data = await state.get_data()
    try:
        await orm_AddActiveUser(session, data)


        await message.answer('Регистрация успешно пройдена.')

        # await message.answer(str(data))
        result_answer = f"""
            ФИО: {list(data.values())[0]}
            Школа: {list(data.values())[1]}
            Номер телефона: {list(data.values())[2]}
            электронная почта: {list(data.values())[3]}
            ФИО наставника: {list(data.values())[4]}
            {"Должность наставника: " + str(list(data.values())[5]) if list(data.values())[5] else ''}"""

        await message.answer(result_answer)
        await message.answer('Открываю меню...', reply_markup=reply.menu_kb)
        await state.clear()
    except Exception as e:
        await message.answer("Что-то пошло не так... Попробуйте позже")
        await state.clear()


#Обработка Инлайн клавиатур
@user_private_router.callback_query(AddUser.status_mentor)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext, session:AsyncSession):
    role = callback_query.data.split('_')[1]
    await callback_query.answer()
    if role == 'teacher':
        await callback_query.message.answer('Введите должность вашего наставника.')
        await state.set_state(AddUser.post_mentor)
    elif role == 'other':
        await callback_query.message.answer('Введите роль вашего наставника.')
        await state.set_state(AddUser.input_status_mentor)
    else:
        await state.update_data(post_mentor='Родитель/опекун')
        await register_step_finish(message=callback_query.message, state=state, session=session)



