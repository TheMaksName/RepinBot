import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers.news_channel import news_channel_router
from app.bot.middlewares.db import DataBaseSession

from app.database.engine import create_db, drop_db, session_maker

from app.bot.handlers.admin_private import admin_private_router
from app.bot.handlers.user_private import user_private_router



from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeAllPrivateChats, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.FSM.FSM_user_private import User_MainStates
from app.bot.FSM.FSM_admin_private import Admin_MainStates

from config import settings

from app.database.orm_query import orm_Check_avail_user, orm_AddUser, orm_Check_register_user, orm_get_all_user
from app.kbds import reply
from app.kbds.reply import admin_kb

from app.bot.common.bot_cmds_list import private
# ALLOWED_UPDATES = ['message', 'callback_query']

bot = Bot(token=settings.BOT_TOKEN)


dp = Dispatcher()


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()

async def on_shutdown(bot):

    print('Бот лег')



dp.include_router(user_private_router)
# dp.include_router(admin_private_router)
dp.include_router(news_channel_router)

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    try:
        if not await orm_Check_avail_user(session, message.from_user.id):
            info_user = dict()
            info_user['user_id'] = message.from_user.id
            info_user['nickname'] = message.from_user.username or 'не установлен'
            await orm_AddUser(session, info_user)

        if settings.PROD:
            user_name = await orm_Check_register_user(session, message.from_user.id)
            if not user_name:

                await message.answer("Здесь должен быть приветственный текст. Появится позже...",
                                     reply_markup=reply.start_kb_prod)
            else:
                await state.set_state(User_MainStates.after_registration)
                await message.answer(f"Привет {user_name.split(" ")[1]}, давно не виделись", reply_markup=reply.menu_kb)

        else:
            await state.set_state(User_MainStates.before_registration)

            await message.answer("""
📢 Приветствие участникам конкурса «РЕПИН НАШ!»
🔹 Почему вы здесь?
Ты, наверное, слышал про Илью Репина — великого художника, автора «Бурлаков на Волге». Но вот странность: в финском музее «Атенеум» вдруг решили, что Репин — не русский художник, а украинский. Как так? Ведь он сам писал, что его вдохновила русская Волга, что он увидел в бурлаках силу и характер русского народа!
Что мы будем с этим делать? Ответ простой: показать, что Репин – наш!
🔹 Зачем этот конкурс?
Мы не просто будем говорить, а докажем историческую правду через цифровое искусство. Ты сможешь создать виртуальную выставку, где расскажешь о Репине и его связи с Самарой, Волгой, бурлаками, русской культурой. Это твой шанс стать художником, исследователем и рассказчиком одновременно!
🔹 Ты точно справишься!
Мы верим в тебя! У тебя уже есть всё, чтобы создать крутой проект:
✅ Наставники – лучшие эксперты помогут и подскажут.
✅ Материалы – вся нужная информация о Репине, Самаре и истории есть в этом боте.
✅ Пошаговые инструкции – мы будем вести тебя от выбора идеи до создания выставки.
✅ Современные технологии – ты попробуешь 3D-моделирование, нейросети, интерактивные элементы.
🔹 Что делать дальше?
💡 Прочитай условия конкурса.
💡 Выбери свою тему – тебя ждёт 30 идей!
💡 Следи за нашими постами – мы расскажем, как создать выставку шаг за шагом.
📢 Репин наш! Самара – его вдохновение! А ты – тот, кто покажет это миру! 🚀
            """, reply_markup=reply.start_kb_not_prod)


    except Exception as e:
        await message.answer("Извините, что-то пошло не так. Попробуйте позже")

@user_private_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer("Открываю меню...", reply_markup=reply.menu_kb)

async def main():

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())

