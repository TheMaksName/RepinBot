
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import ActiveUser, AllUser, News, Admins, Themes, Materials


# Добавление активного пользователя
async def orm_AddActiveUser(session: AsyncSession, data: dict):
    """
    Добавляет активного пользователя в базу данных.

    :param session: Асинхронная сессия SQLAlchemy.
    :param data: Словарь с данными пользователя.
    """
    obj = ActiveUser(
        user_id=data['user_id'],
        name=data['name_user'],
        school=data['school'],
        phone_number=data['phone_number'],
        mail=data['mail'],
        name_mentor=data['name_mentor'],
        post_mentor=data['post_mentor'],
    )
    session.add(obj)
    await session.commit()


# Добавление пользователя
async def orm_AddUser(session: AsyncSession, data: dict):
    """
    Добавляет пользователя в базу данных.

    :param session: Асинхронная сессия SQLAlchemy.
    :param data: Словарь с данными пользователя.
    """
    obj = AllUser(
        user_id=data['user_id'],
        nickname=data['nickname'],
        reg_status=False
    )
    session.add(obj)
    await session.commit()


# Получение всех пользователей
async def orm_get_all_user(session: AsyncSession):
    """
    Возвращает список всех user_id из таблицы AllUser.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список user_id.
    """
    query = select(AllUser.user_id)
    result = await session.execute(query)
    return result.scalars()


# Изменение статуса регистрации пользователя
async def orm_Change_RegStaus(session: AsyncSession, user_id: int, new_reg_status: bool):
    """
    Изменяет статус регистрации пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param new_reg_status: Новый статус регистрации.
    """
    query = update(AllUser).where(AllUser.user_id == user_id).values(
        reg_status=new_reg_status
    )
    await session.execute(query)
    await session.commit()


# Проверка наличия пользователя
async def orm_Check_avail_user(session: AsyncSession, user_id: int):
    """
    Проверяет, существует ли пользователь с указанным user_id.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Идентификатор пользователя, если он существует, иначе None.
    """
    query = select(AllUser.id).where(AllUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# Проверка регистрации пользователя
async def orm_Check_register_user(session: AsyncSession, user_id: int):
    """
    Проверяет, зарегистрирован ли пользователь как активный.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Имя пользователя, если он зарегистрирован, иначе None.
    """
    query = select(ActiveUser.name).where(ActiveUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# Получение информации о пользователе
async def orm_Get_info_user(session: AsyncSession, user_id: int):
    """
    Возвращает информацию о пользователе.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Объект ActiveUser, если пользователь найден, иначе None.
    """
    query = select(ActiveUser).where(ActiveUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# Редактирование профиля пользователя
async def orm_Edit_user_profile(session: AsyncSession, user_id: int, data: dict):
    """
    Редактирует профиль пользователя.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param data: Словарь с данными для обновления.
    """
    try:
        data = list(*data.items())
        field = data[0][5:]
        print(field)
        value = data[1]
        query = update(ActiveUser).where(ActiveUser.user_id == user_id).values(
            {field: value}
        )
        await session.execute(query)
        await session.commit()
    except Exception as e:
        print(f"Ошибка при редактировании профиля: {e}")


# Добавление администратора
async def orm_add_admin(session: AsyncSession, user_id: int, username: str):
    """
    Добавляет администратора в базу данных.

    :param session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор администратора.
    :param username: Никнейм администратора.
    """
    obj = Admins(
        user_id=user_id,
        nickname=username
    )
    session.add(obj)
    await session.commit()


# Получение списка администраторов
async def orm_get_list_admin(session: AsyncSession):
    """
    Возвращает список всех user_id администраторов.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список user_id администраторов.
    """
    query = select(Admins.user_id)
    result = await session.execute(query)
    return result.scalars().all()


# Добавление новости
async def orm_add_news(session: AsyncSession, post_id: int, text: str, photo: str):
    """
    Добавляет новость в базу данных.

    :param session: Асинхронная сессия SQLAlchemy.
    :param post_id: Идентификатор поста.
    :param text: Текст новости.
    :param photo: Ссылка на изображение.
    """
    obj = News(
        post_id=post_id,
        text=text,
        image=photo
    )
    session.add(obj)
    await session.commit()


# Получение новости по идентификатору
async def orm_get_news_by_id(session: AsyncSession, id: int):
    """
    Возвращает новость по её идентификатору.

    :param session: Асинхронная сессия SQLAlchemy.
    :param id: Идентификатор новости.
    :return: Объект News, если новость найдена, иначе None.
    """
    query = select(News).where(News.id == id)
    result = await session.execute(query)
    return result.scalar()


# Редактирование новости
async def orm_edit_news_by_id(session: AsyncSession, post_id: int, text: str = None, photo: str = None):
    """
    Редактирует новость по её идентификатору.

    :param session: Асинхронная сессия SQLAlchemy.
    :param post_id: Идентификатор поста.
    :param text: Новый текст новости.
    :param photo: Новая ссылка на изображение.
    """
    if text and photo:
        query = update(News).where(News.post_id == post_id).values(text=text, image=photo)
    elif text:
        query = update(News).where(News.post_id == post_id).values(text=text)
    elif photo:
        query = update(News).where(News.post_id == post_id).values(image=photo)
    await session.execute(query)
    await session.commit()


# Получение всех новостей
async def orm_get_all_news(session: AsyncSession):
    """
    Возвращает список всех новостей.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Список объектов News.
    """
    query = select(News)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_all_themes_by_category_id(session:AsyncSession, category_id: int):
    query = select(Themes).options(selectinload(Themes.category)).where(Themes.category_id == category_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_theme_by_id(session: AsyncSession, theme_id: int):
    query = select(Themes).where(Themes.id == theme_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_material_by_id(session: AsyncSession, material_id: int):
    query = select(Materials).where((Materials.id >= 1+5*material_id) & (Materials.id <= (material_id+1)*5))
    result = await session.execute(query)
    return result.scalars().all()