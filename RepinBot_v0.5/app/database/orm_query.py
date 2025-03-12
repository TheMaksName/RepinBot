
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ActiveUser, AllUser



async def orm_AddActiveUser(session: AsyncSession, data):
    obj = ActiveUser(
        user_id = data['user_id'],
        name=data['name_user'],
        school=data['school'],
        phone_number=data['phone_number'],
        mail=data['mail'],
        name_mentor=data['name_mentor'],
        post_mentor=data['post_mentor'],
    )
    session.add(obj)
    await session.commit()

async def orm_AddUser(session: AsyncSession, data):
    obj = AllUser(
        user_id = data['user_id'],
        nickname = data['nickname'],
        reg_status = False
    )

    session.add(obj)
    await session.commit()
async def orm_get_all_user(session: AsyncSession):
    query = select(AllUser.user_id)
    result = await session.execute(query)
    return result.scalar()
async def orm_Change_RegStaus(session: AsyncSession, user_id: int, new_reg_status: bool):
    query = update(AllUser).where(AllUser.user_id == user_id).values(
        reg_status = new_reg_status
    )

    await session.execute(query)
    await session.commit()
async def orm_Check_avail_user(session: AsyncSession, user_id: int):
    query = select(AllUser.id).where(AllUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()
async def orm_Check_register_user(session: AsyncSession, user_id: int):
    query = select(ActiveUser.name).where(ActiveUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()
async def orm_Get_info_user(session: AsyncSession, user_id:int):
    query = select(ActiveUser).where(ActiveUser.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()
async def orm_Edit_user_profile(session: AsyncSession, user_id: int, data: dict):

    try:
        data = list(*data.items())
        print('1', data[0].lstrip('edit_'))
        query = update(ActiveUser).where(ActiveUser.user_id == user_id).values(
            {f'{data[0].lstrip('edit_')}':f'{data[1]}'}
        )
        await session.execute(query)
        await session.commit()
    except Exception as e:
        print(e)
