from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    caches = {"default": TTLCache(maxsize=10_000, ttl=0.2)}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any],
    ) -> Any:
        throttling_key = "default"
        usr = message.from_user.id
        if throttling_key is not None and throttling_key in self.caches:
            if usr in self.caches[throttling_key]:
                await message.answer("Слишком много запросов. Попробуйте позже.")
                return
            else:
                self.caches[throttling_key][usr] = None
        return await handler(message, data)
