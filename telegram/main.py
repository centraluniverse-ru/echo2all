import sqlalchemy as sa
from aiogram import Bot, Dispatcher, types, enums, client
from telegram.routes.service import service_router
from telegram.routes.user import user_router
from telegram.routes.admin.main import admin_router
from telegram.middlewares.throttling import ThrottlingMiddleware
from utils.telegram import bot
from logs.main import logger

dp = Dispatcher()
dp.include_routers(service_router, admin_router, user_router)
# dp.message.middleware.register(ThrottlingMiddleware())


async def main() -> None:
    await dp.start_polling(bot)
    logger.info("Bot started")


async def stop_pooling() -> None:
    await dp.stop_polling()
    logger.info("Bot stopped")
