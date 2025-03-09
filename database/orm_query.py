from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ActiveUser


async def orm_AddActiveUser(session: AsyncSession, data):
    obj = ActiveUser(
        name=data['name_user'],
        school=data['school'],
        phone_number=data['phone_number'],
        email=data['email'],
        name_mentor=data['name_mentor'],
        post_mentor=data['post_mentor'],
    )
    session.add(obj)
    await session.commit()