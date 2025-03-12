from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from sqlalchemy.ext.asyncio import AsyncSession


from app.bot.FSM.FSM_user_private import RegistrationUser, MainStates
from app.bot.common.validation import validate_fio, validate_phone_number, validate_email_format
from app.bot.common.verif_mail import start_verify_mail, \
    check_verify_code
from app.bot.kbds import reply
from app.bot.kbds.inline import role_inline_kb
from app.database.orm_query import orm_Change_RegStaus, orm_AddActiveUser

user_registration_router = Router()

#Код ниже для машины состояний (FSM) для регистрации участника
@user_registration_router.message(RegistrationUser.name_user)
async def register_step_name(message: Message, state: FSMContext):
    if validate_fio(message.text.strip()):
        await message.answer('Введите полное название вашей школы')
        await state.update_data(name_user=message.text)
        await state.set_state(RegistrationUser.school)
    else:
        await message.answer("Пожалуйста, введи ФИО в правильном формате (Фамилия Имя Отчество).")

@user_registration_router.message(RegistrationUser.school)
async def register_step_phone_number(message: Message, state: FSMContext):

    await state.update_data(school=message.text)
    await message.answer('Введите номер Вашего телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')
    await state.set_state(RegistrationUser.phone_number)


@user_registration_router.message(RegistrationUser.phone_number, F.text)
async def register_step_mail(message: Message, state: FSMContext):
    phone_number = message.text
    if validate_phone_number(phone_number):
        await state.update_data(phone_number=message.text)
        await message.answer('Введите адрес Вашей электронной почты')
        await state.set_state(RegistrationUser.mail)
    else:
        await message.answer("Пожалуйста, введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.")


@user_registration_router.message(RegistrationUser.mail, F.text)
async def register_step_name_mentor(message: Message, state: FSMContext):
    try:
        if validate_email_format(email=message.text):
            await state.update_data(mail=message.text)
            await start_verify_mail(message.text, message.from_user.id)
            await state.set_state(RegistrationUser.verify_mail)
            await message.answer(text="На вашу почту был отправлен код подтверждения. Пожалуйста введите код")
        else:
            await message.answer(text="Неверный формат электронной почты. Пожалуйста введите почту в правильном формате")
    except Exception as e:
        pass


@user_registration_router.message(RegistrationUser.verify_mail, F.text)
async def register_step_verify_mail(message: Message, state: FSMContext):
    if check_verify_code(message.text, message.from_user.id):
        await message.answer(text="Подтверждение почты успешно пройдено")
        await message.answer('Введите полное ФИО Вашего наставника в формате (Фамилия Имя Отчество)')
        await state.set_state(RegistrationUser.name_mentor)
    else:
        await message.answer(text="Введен неправильный код. Попробуйте еще раз")

@user_registration_router.message(RegistrationUser.name_mentor, F.text)
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

@user_registration_router.message(RegistrationUser.input_status_mentor)
async def register_input_status_mentor(message: Message, state: FSMContext, session:AsyncSession):
    await state.update_data(post_mentor=message.text)
    await register_step_finish(message=message, state=state, session=session)

@user_registration_router.message(RegistrationUser.post_mentor)
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
            электронная почта: {data['mail']}
            ФИО наставника: {data['name_mentor']}
            {"Должность наставника: " + data['post_mentor'] if data['post_mentor'] else ''}"""

        await message.answer(result_answer)
        await message.answer('Открываю меню...', reply_markup=reply.menu_kb)
        await state.set_state(MainStates.after_registration)
        await state.set_data({})

    except Exception as e:
        await message.answer("Что-то пошло не так... Попробуйте позже")
        await state.clear()


#Обработка Инлайн при регистрации пользователя
@user_registration_router.callback_query(RegistrationUser.status_mentor)
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
