from aiogram import Bot, enums, client
from utils.constants import TOKEN

bot = Bot(
    token=TOKEN,
    default=client.default.DefaultBotProperties(parse_mode=enums.ParseMode.HTML),
)
