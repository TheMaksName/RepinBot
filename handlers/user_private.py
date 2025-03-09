from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command


from sqlalchemy.ext.asyncio import AsyncSession

from FSM.FSM_user_private import RegistrationUser, MainStates, EditProfile
from common.validation import validate_fio, validate_phone_number
from database.orm_query import orm_AddActiveUser, orm_AddUser, orm_Change_RegStaus, \
    orm_Get_info_user, orm_Check_register_user, orm_Check_avail_user
from kbds import reply
from kbds.inline import role_inline_kb, get_callback_btns

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    try:
        if not await orm_Check_avail_user(session, message.from_user.id):
            info_user = dict()
            info_user['user_id'] = message.from_user.id
            info_user['nickname'] = message.from_user.username or 'не установлен'
            await orm_AddUser(session, info_user)

        user_name = await orm_Check_register_user(session, message.from_user.id)
        print(user_name)
        if not user_name:
            await state.set_state(MainStates.before_registration)
            await message.answer("Здесь должен быть приветственный текст. Появится позже...",
                                 reply_markup=reply.start_kb)
        else:
            await state.set_state(MainStates.after_registration)
            await message.answer(f"Привет {user_name.split(" ")[1]}, давно не виделись", reply_markup=reply.menu_kb)
    except Exception as e:
        await message.answer("Извините, что-то пошло не так. Попробуйте позже")

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
    reply_markup=get_callback_btns(
        btns={
            "Редактировать": f"edit_profile"
        }
        )
    await message.answer(result_answer, reply_markup=reply_markup)

@user_private_router.callback_query(MainStates.after_registration)
@user_private_router.callback_query(F.data.startswith("edit_"))
async def change_edit_profile_callback(callback_query: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if callback_query.data.lstrip('edit_') == 'profile':
        reply_markup = get_callback_btns(
            btns={
                "Редактировать ФИО": f"edit_profile_name",
                "Редактировать название школы": f"edit_profile_school",
                "Редактировать номер телефона": f"edit_profile_phone_number",
                "Редактировать электронную почту": f"edit_profile_email",
                "Редактировать ФИО наставника": f"edit_profile_name_mentor",
                "Редактировать должность наставника": f"edit_profile_post_mentor",
                "Назад": f"edit_back"

            }
            )
        await callback_query.message.edit_reply_markup(reply_markup=reply_markup)
    elif callback_query.data.lstrip('edit_') == 'profile_name':
        await state.set_state(EditProfile.edit_name)
        await callback_query.message.answer("Введи новое ФИО")
    elif callback_query.data.lstrip('edit_') == 'profile_school':
        await state.set_state(EditProfile.edit_school)
        await callback_query.message.answer("Введи новое название школы")
    elif callback_query.data.lstrip('edit_') == 'profile_phone_number':
        await state.set_state(EditProfile.edit_phone_number)
        await callback_query.message.answer("Введи новый номер телефона")
    elif callback_query.data.lstrip('edit_') == 'profile_email':
        await state.set_state(EditProfile.edite_mail)
        await callback_query.message.answer("Введи новую почту")
    elif callback_query.data.lstrip('edit_') == 'profile_name_mentor':
        await state.set_state(EditProfile.edit_name_mentor)
        await callback_query.message.answer("Введи новое ФИО наставника")
    elif callback_query.data.lstrip('edit_') == 'profile_post_mentor':
        await state.set_state(EditProfile.edit_post_mentor)
        await callback_query.message.answer("Введи новую должность наставника")
    elif callback_query.data.lstrip('edit_') == 'back':
        reply_markup = get_callback_btns(
            btns={
                "Редактировать": f"edit_profile"
            }
        )
        await state.set_state(MainStates.after_registration)
        await callback_query.message.edit_reply_markup(reply_markup=reply_markup)

@user_private_router.message(StateFilter(EditProfile.edit_name, EditProfile.edit_school,
                                         EditProfile.edite_mail, EditProfile.edit_name_mentor,
                                         EditProfile.edit_post_mentor, EditProfile.edit_phone_number,))
async def edit_profile(message: Message, session: AsyncSession, state: FSMContext):
    current_state = str(await state.get_state()).lstrip("EditProfile")
    if current_state == ':edit_name':
        await message.answer(f"Вы изменили имя на: {message.text}")
        await state.set_state(MainStates.after_registration)
    elif current_state == ':edit_school':
        await message.answer(f"Вы изменили навзвание школы на: {message.text}")
        await state.set_state(MainStates.after_registration)
    elif current_state == ':edit_phone_number':
        await message.answer(f"Вы изменили номер телефона на: {message.text}")
        await state.set_state(MainStates.after_registration)
    elif current_state == ':edit_mail':
        await message.answer(f"Вы изменили адрес электронной почты на: {message.text}")
        await state.set_state(MainStates.after_registration)
    elif current_state == ':edit_name_mentor':
        await message.answer(f"Вы изменили имя наставника на: {message.text}")
        await state.set_state(MainStates.after_registration)
    elif current_state == ':edit_post_mentor':
        await message.answer(f"Вы изменили должность наставника на: {message.text}")
        await state.set_state(MainStates.after_registration)


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




    try:
        if user_id:
            await state.update_data(user_id=user_id)
            await orm_Change_RegStaus(session, user_id, True)
        else:
            await state.update_data(user_id=message.from_user.id)
            await orm_Change_RegStaus(session, message.from_user.id, True)
        data = await state.get_data()
        print(data)
        await message.answer('Регистрация успешно пройдена.')
        await orm_AddActiveUser(session, data)
        result_answer = f"""
            ФИО: {data['name_user']}
            Школа: {data['school']}
            Номер телефона: {data['phone_number']}
            электронная почта: {data['email']}
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


