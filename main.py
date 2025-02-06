import asyncio
from telegram.main import main as telegram_bot_task
from logs.main import logger
from utils.telegram import bot
from aiogram import exceptions


if __name__ == "__main__":
    logger.info("Starting the app")
    asyncio.run(telegram_bot_task())
