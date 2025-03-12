import asyncio


from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats

from app.config import settings

from app.database.engine import create_db, drop_db, session_maker

from app.bot.middlewares.db import DataBaseSession

from app.bot.handlers.user_private import user_private_router
from app.bot.common.bot_cmds_list import private

# ALLOWED_UPDATES = ['message', 'callback_query']

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(user_private_router)

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()

async def on_shutdown(bot):

    print('Бот лег')

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())