from aiogram import BaseMiddleware, types, exceptions
import typing
from db import database
from utils.telegram import bot


class UserMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: typing.Callable[
            [types.Message, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]
        ],
        event: types.Message,
        data: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        user = database.get_or_create_user(event.from_user.id, event.from_user.username)
        try:
            await bot.send_chat_action(user.telegram_id, "typing")
            database.set_is_banned_bot(telegram_id=event.from_user.id, is_banned=False)
        except exceptions.TelegramForbiddenError:
            database.set_is_banned_bot(telegram_id=event.from_user.id, is_banned=True)
        data["user"] = user
        return await handler(event, data)
