from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.FSM.FSM_user_private import RegistrationUser, User_MainStates
from app.bot.handlers.user_edit_profile import user_view_profile_router
from app.bot.handlers.user_registartion import user_registration_router
from app.kbds.inline import get_callback_btns
from app.kbds.reply import get_keyboard
from app.database.orm_query import orm_Get_info_user, orm_get_news_by_id, orm_get_all_news, \
    orm_get_all_themes_by_category_id, orm_get_theme_by_id, orm_Edit_user_profile, orm_get_material_by_id
from app.kbds import reply
from config import settings

# Создаем роутер для приватных команд пользователя
user_private_router = Router()
user_private_router.include_router(user_registration_router)
user_private_router.include_router(user_view_profile_router)

# Кэш для хранения текущей новости и темы для каждого пользователя
cache_current_news = {}
cache_current_theme = {}
cache_current_material = {}

# Команда /menu для открытия меню
@user_private_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer("Открываю меню...", reply_markup=reply.menu_kb)

# Обработчик для команды "новости"
@user_private_router.message(F.text.lower() == 'новости')
async def news(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    cache_current_news[user_id] = 1  # Устанавливаем начальную новость
    news = await orm_get_news_by_id(session=session, id=1)  # Получаем первую новость

    if news:
        reply_keyboard = get_callback_btns(btns={"Далее": 'news_next'})
        if news.image.lower() != 'без фото':
            await message.answer_photo(
                news.image,
                caption=f'<strong>{news.text}</strong>',
                parse_mode='HTML',
                reply_markup=reply_keyboard
            )
        else:
            await message.answer(news.text, reply_markup=reply_keyboard)
        await message.answer("Вот последние новости:")
    else:
        await message.answer("Новостей пока нет(((")

# Обработчик для переключения между новостями
@user_private_router.callback_query(F.data.startswith('news_'))
async def slide_news(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    action = callback.data.split("_")[1]  # Определяем действие (next или back)
    current_news_id = cache_current_news.get(user_id, 1)

    if action == 'next':
        current_news_id += 1
    elif action == 'back':
        current_news_id = max(1, current_news_id - 1)  # Не опускаемся ниже первой новости

    cache_current_news[user_id] = current_news_id
    news = await orm_get_news_by_id(session=session, id=current_news_id)

    if news:
        # Определяем, есть ли следующая новость
        next_news_exists = await orm_get_news_by_id(session=session, id=current_news_id + 1)
        reply_keyboard = get_callback_btns(
            btns={
                "Назад": 'news_back',
                "Далее": 'news_next' if next_news_exists else None,
            }
        )
        await callback.message.edit_media(
            media=InputMediaPhoto(media=news.image, caption=news.text),
            reply_markup=reply_keyboard
        )
    else:
        await callback.answer("Новостей больше нет")

# Обработчик для команды "материалы"
@user_private_router.message(StateFilter(User_MainStates.after_registration,User_MainStates.before_registration), F.text.lower() == 'материалы')
async def get_material(message: Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    cache_current_material[user_id] = 0  # Устанавливаем начальную тему
    materials = await orm_get_material_by_id(session=session, material_id=0)

    if materials:

        btns = {f'Материал №{material.id}': f'choice_material_{material.id}' for material in materials}

        btns.update({"Далее": "slide_material_next"})
        reply_markup = get_callback_btns(btns=btns, sizes=(3, 3, 2))

        result_answer = ""
        for material in materials:
            result_answer += f'{material.id}🟦 {material.title}\n'

        await message.answer(f"Вывожу список материалов.\n\n{result_answer}", reply_markup=reply_markup)
    else:
        await message.answer("Материалы пока отсутствуют")


@user_private_router.callback_query(F.data.startswith('slide_material_'))
async def choice_theme(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    action = callback.data.split('_')[2]  # Определяем действие (next или back)
    current_category_id = cache_current_material.get(user_id, 1)

    if action == 'next':
        current_category_id += 1
    elif action == 'back':
        current_category_id = max(0, current_category_id - 1)  # Не опускаемся ниже первой категории

    cache_current_theme[user_id] = current_category_id
    materials = await orm_get_material_by_id(session=session, material_id=current_category_id)

    if materials:
        # Проверяем, есть ли следующая категория
        next_materials_exists = await orm_get_material_by_id(session=session, material_id=current_category_id + 1)
        # Проверяем, есть ли предыдущая категория
        prev_materials_exists = await orm_get_material_by_id(session=session, material_id=current_category_id - 1)

        # Создаем кнопки для тем

        btns = {f'Материал №{material.id}': f'choice_material_{material.id}' for material in materials}


        # Добавляем кнопку "Назад", если это не первая категория
        if prev_materials_exists:
            btns.update({"Назад": "slide_material_back"})

        # Добавляем кнопку "Далее", если это не последняя категория
        if next_materials_exists:
            btns.update({"Далее": "slide_material_next"})

        # Создаем клавиатуру
        reply_markup = get_callback_btns(btns=btns, sizes=(3, 3, 2))

        # Формируем текст с информацией о темах
        result_answer = ""
        for material in materials:
            result_answer += f'{material.id}🟦 {material.title}\n'

        await callback.message.edit_text(f"Вывожу список материалов.\n\n{result_answer}", reply_markup=reply_markup)
    else:
        await callback.answer("Материалы пока отсутствуют")





# Обработчик для команды "выбрать тему"
@user_private_router.message(StateFilter(User_MainStates.after_registration,User_MainStates.before_registration), F.text.lower() == 'посмотреть темы')
async def get_material(message: Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    cache_current_theme[user_id] = 1  # Устанавливаем начальную тему
    themes = await orm_get_all_themes_by_category_id(session=session, category_id=1)

    if themes:
        if settings.PROD:
            btns = {f'Тема №{theme.id}': f'choice_theme_{theme.id}' for theme in themes}
        else:
            btns = {}
        btns.update({"Далее": "slide_theme_next"})
        reply_markup = get_callback_btns(btns=btns, sizes=(3, 3, 2))

        result_answer = f"Категория: {themes[0].category.title}\n\n"
        for theme in themes:
            result_answer += (f'{theme.id}🟦 {theme.title}\n'
                             f'📌Прием: {theme.technique}\n\n')

        await message.answer(f"Вывожу список тем.\n\n{result_answer}", reply_markup=reply_markup)
    else:
        await message.answer("Темы пока отсутствуют")

# Обработчик для переключения между темами
@user_private_router.callback_query(F.data.startswith('slide_theme_'))
async def choice_theme(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    action = callback.data.split('_')[2]  # Определяем действие (next или back)
    current_category_id = cache_current_theme.get(user_id, 1)

    if action == 'next':
        current_category_id += 1
    elif action == 'back':
        current_category_id = max(1, current_category_id - 1)  # Не опускаемся ниже первой категории

    cache_current_theme[user_id] = current_category_id
    themes = await orm_get_all_themes_by_category_id(session=session, category_id=current_category_id)

    if themes:
        # Проверяем, есть ли следующая категория
        next_category_exists = await orm_get_all_themes_by_category_id(session=session, category_id=current_category_id + 1)
        # Проверяем, есть ли предыдущая категория
        prev_category_exists = await orm_get_all_themes_by_category_id(session=session, category_id=current_category_id - 1)

        # Создаем кнопки для тем
        if settings.PROD:
            btns = {f'Тема №{theme.id}': f'choice_theme_{theme.id}' for theme in themes}
        else:
            btns = {}

        # Добавляем кнопку "Назад", если это не первая категория
        if prev_category_exists:
            btns.update({"Назад": "slide_theme_back"})

        # Добавляем кнопку "Далее", если это не последняя категория
        if next_category_exists:
            btns.update({"Далее": "slide_theme_next"})

        # Создаем клавиатуру
        reply_markup = get_callback_btns(btns=btns, sizes=(3, 3, 2))

        # Формируем текст с информацией о темах
        result_answer = f"Категория: {themes[0].category.title}\n\n"
        for theme in themes:
            result_answer += (f'{theme.id}🟦 {theme.title}'
                             f'📌Прием: {theme.technique}\n\n')

        # Редактируем сообщение с новыми данными
        await callback.message.edit_text(f"Вывожу список тем.\n\n{result_answer}", reply_markup=reply_markup)
    else:
        await callback.answer("Темы в этой категории отсутствуют")

@user_private_router.callback_query(F.data.startswith('choice_theme_'))
async def choice_theme(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    theme_id = int(callback.data.split('_')[2])
    current_theme = await orm_get_theme_by_id(session=session, theme_id=theme_id)

    await state.update_data(prev_message_id=callback.message.message_id)

    reply_markup = get_callback_btns(
        btns={
            "Подверждаю✅": f"confirm_theme_{theme_id}",
            "Я передумал❌": "confirm_theme_"
        }
    )

    await callback.message.answer(text=f"Вы выбираете тему:\n\n"
                                       f"🟦 {current_theme.title}\n"
                                       f"📌Прием: {current_theme.technique}\n\n"
                                       f"Подтверждаете выбор?",reply_markup=reply_markup)

@user_private_router.callback_query(F.data.startswith("confirm_theme_"))
async def confirm_theme(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    confirm_theme_id = callback.data.split("_")[2]
    if confirm_theme_id:
        user_id = callback.from_user.id
        current_theme = await orm_get_theme_by_id(session=session, theme_id=int(confirm_theme_id))
        data = {'edit_theme': f'{current_theme.title} {current_theme.technique}'}
        await orm_Edit_user_profile(session=session, user_id=user_id, data=data)

        message_ids_to_delete = []
        state_data = await state.get_data()
        prev_message_id = state_data.get("prev_message_id")

        # Добавляем текущее сообщение в список для удаления
        message_ids_to_delete.append(callback.message.message_id)
        message_ids_to_delete.append(prev_message_id)

        await callback.bot.delete_messages(callback.message.chat.id, message_ids_to_delete)


        await callback.message.answer("Тема успешна выбрана📥")
    else:
        await callback.message.delete()

# Обработчик для команды "мой профиль"
@user_private_router.message(User_MainStates.after_registration, F.text.lower() == 'мой профиль')
async def get_user_profile(message: Message, session: AsyncSession, state: FSMContext):
    await state.set_state(User_MainStates.user_view_profile)
    data = await orm_Get_info_user(session, message.from_user.id)
    if data:
        result_answer = (f"📄ФИО: {data.name}\n"
                        f"🏫Школа: {data.school}\n"
                        f"📱Номер телефона: {data.phone_number}\n"
                        f"📧Электронная почта: {data.mail}\n"
                        f"👨‍🏫ФИО наставника: {data.name_mentor}\n"
                        f"👪Должность наставника: {data.post_mentor if data.post_mentor else ''}\n"
                        f"📜Тема: {data.theme}")

        reply_markup = get_keyboard(
            "Редактировать",
            "Назад",
            placeholder="Выберите действие",
            sizes=(2,),
        )
        await message.answer("Открываю Ваш профиль")
        await message.answer(result_answer, reply_markup=reply_markup)
    else:
        await message.answer("Профиль не найден")

# Обработчик для команды "зарегистрироваться"
@user_private_router.message(User_MainStates.before_registration)
async def process_action(message: Message, state: FSMContext):
    if message.text.lower() == 'зарегистрироваться':
        await message.answer("Отлично, давай регистрироваться)))", reply_markup=reply.del_kbd)
        await message.answer('Введите Ваше ФИО в формате (Фамилия Имя Отчество)')
        await state.set_state(RegistrationUser.name_user)




# @user_private_router.message(Command('admin'))
# async def admin(message: Message, session: AsyncSession, state: FSMContext):
#     list_admins = list(await orm_get_list_admin(session=session))
#     print(list_admins)
#     if message.from_user.username == settings.USER_ADMIN_NICK or message.from_user.id in list_admins:
#         reply_markup = admin_kb
#         if message.from_user.id not in list_admins:
#             await orm_add_admin(session=session, user_id=message.from_user.id, username=message.from_user.username)
#         if message.from_user.username == settings.USER_ADMIN_NICK:
#             reply_markup = admin_kb
#             reply_markup.keyboard[1].append(KeyboardButton(text="Добавить админа"))
#         await message.answer(text="Вы вошли как админ", reply_markup=reply_markup)
#         await state.set_state(Admin_MainStates.choice_action)
#     else:
#         await message.answer(text="У вас недостаточно прав")


