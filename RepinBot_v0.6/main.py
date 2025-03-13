import asyncio

from aiogram import Bot, Dispatcher

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

from app.database.orm_query import  orm_Check_avail_user, orm_AddUser, orm_Check_register_user
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
    print(1)
    await create_db()

async def on_shutdown(bot):
    print('Бот лег')



dp.include_router(user_private_router)
dp.include_router(admin_private_router)

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    if message.from_user.username == settings.USER_ADMIN_NICK:
        await message.answer("Привет Админ!", reply_markup=admin_kb)
        await state.set_state(Admin_MainStates.choice_action)
    else:
        try:
            if not await orm_Check_avail_user(session, message.from_user.id):
                info_user = dict()
                info_user['user_id'] = message.from_user.id
                info_user['nickname'] = message.from_user.username or 'не установлен'
                await orm_AddUser(session, info_user)

            user_name = await orm_Check_register_user(session, message.from_user.id)
            if not user_name:
                await state.set_state(User_MainStates.before_registration)
                await message.answer("Здесь должен быть приветственный текст. Появится позже...",
                                     reply_markup=reply.start_kb)
            else:
                await state.set_state(User_MainStates.after_registration)
                await message.answer(f"Привет {user_name.split(" ")[1]}, давно не виделись", reply_markup=reply.menu_kb)

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

