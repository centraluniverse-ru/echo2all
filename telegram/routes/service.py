from aiogram import Router, enums, types
from db import database

service_router = Router(name=__name__)


@service_router.my_chat_member()
async def chatmemberupdated(update: types.ChatMemberUpdated) -> None:
    if update.new_chat_member.status == enums.ChatMemberStatus.KICKED:
        database.set_is_banned_bot(update.from_user.id, True)
    if update.new_chat_member.status == enums.ChatMemberStatus.MEMBER:
        database.set_is_banned_bot(update.from_user.id, False)
