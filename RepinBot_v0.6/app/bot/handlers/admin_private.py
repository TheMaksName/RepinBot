

from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.FSM.FSM_admin_private import Admin_MainStates, AddNews
from app.database.orm_query import orm_add_news
from app.kbds.inline import get_callback_btns

from sqlalchemy.ext.asyncio import AsyncSession

admin_private_router = Router()

@admin_private_router.message(Admin_MainStates.choice_action)
async def choice_action(message: Message, state: FSMContext):
    if message.text.lower() == "редактировать новость":
        await message.answer(text="Я пока не умею редактировать новости((")
    elif message.text.lower() == "создать новость":
        await message.answer(text="Отлично! Новости это хорошо\nВведи заголовок новости")
        await state.set_state(AddNews.add_title)
    else:
        await message.answer(text="Не совсем вас понял")

@admin_private_router.message(AddNews.add_title, F.text)
async def add_title(message: Message, state: FSMContext):
    title = message.text
    if len(title) > 100:
        await message.answer("Название слишком длинное")
    else:

        await state.update_data(add_title=title)
        await message.answer(text="Интересное название. Теперь добавим текст новости.\nНапиши текст новости")
        await state.set_state(AddNews.add_description)

@admin_private_router.message(AddNews.add_description, F.text)
async def add_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(add_description=description)
    await message.answer(text="Отличный текст. Теперь добавим изображение новости.\nПришли изображение для новости")
    await state.set_state(AddNews.add_image)

# async def process_media_group(media_group_id):
#     messages = media_groups.pop(media_group_id)
#     photos_id = []
#     for message in messages:
#         if message.photo:
#             file_id = message.photo[-1].file_id
#             photos_id.append(str(file_id))
#     return photos_id
# media_groups = {}

@admin_private_router.message(AddNews.add_image, F.photo)
async def add_photo(message: Message, state: FSMContext):
    # if message.media_group_id:
    #     media_group_id = message.media_group_id
    #     if media_group_id not in media_groups:
    #         media_groups[media_group_id] = []
    #     media_groups[media_group_id].append(message)
    #     if len(media_groups[media_group_id]) in range(1,11):
    #         photos = await process_media_group(media_group_id)
    #         await state.update_data(add_photo=photos)
    #         print(1)
    #         await message.answer_media_group(media=[InputMediaPhoto(media=photo) for photo in photos])
    # else:
    await state.update_data(add_image=message.photo[-1].file_id)
    data = await state.get_data()
    reply_markup = get_callback_btns(
        btns={
            "Опубликовать": f"publicate",
            "Отменить": f"cancel",
        }
    )
    await message.answer_photo(data['add_image'],
                               caption=f'<strong>{data['add_title']}</strong>\n{data['add_description']}',
                               parse_mode="HTML", reply_markup=reply_markup)
    await state.set_state(AddNews.confirm_add)


@admin_private_router.callback_query(AddNews.confirm_add, F.data == 'publicate')
async def confirm_add_news(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer(text="Новость успешно опубликована!")
    await orm_add_news(session=session, data=await state.get_data())

