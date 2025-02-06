from aiogram import Router, types, filters, html, F, enums
from telegram.middlewares.user import UserMiddleware
from db.models import User
from db import database
from telegram.routes.admin.mailing.sender import MailingTask
from telegram.keyboards.admin import keyboard_for_message
from utils.constants import LOGS
import asyncio
from datetime import datetime
import re

user_router = Router(name=__name__)
user_router.message.middleware(UserMiddleware())


class Dummy:
    pass


@user_router.message(filters.CommandStart(), F.chat.type == "private")
async def command_start_handler(message: types.Message, user: User) -> None:
    await message.answer(
        "Добро пожаловать!\n"
        "Все просто - отправь сообщение мне и я разошлю его всем участникам\n"
        "По умолчанию, ты получаешь новые сообщения. Технически, я могу посмотреть, кто отправил сообщение, но фактически, я не храню отправителя сообщения\n"
        "Ты можешь подписать свои сообщения. Для этого, напиши <code>/sign [name]</code>\n"
        "Чтобы перестать получать сообщения - /stop_receiving\n"
        "Профиль открывается по /profile"
    )


@user_router.message(filters.Command("help"), F.chat.type == "private")
async def command_start_handler(message: types.Message, user: User) -> None:
    await message.answer(
        "/sign [подпись] - Поставить подпись\n"
        "/remove_sign - Удалить подпись\n"
        "/profile - не ебу че это\n"
        "/stop_receiving - заебал бот\n"
        "/start_receiving - не заебал бот\n"
    )


@user_router.message(filters.Command("sign"), F.chat.type == "private")
async def command_sign_handler(message: types.Message, user: User) -> None:
    try:
        signature = " ".join(message.text.split(" ")[1:])
    except:
        await message.answer(
            "Подпись не найдена. Используй <code>/signature [name]</code>, чтобы ее установить"
        )
        return

    if signature == "admin" and user.role != "admin":
        await message.answer("Нельзя использовать эту подпись. Соси хуй.")
        return

    database.update_sign(message.from_user.id, signature)
    await message.answer(
        f"Подпись {html.quote(signature)} установлена. Удалить - /remove_sign"
    )


@user_router.message(filters.Command("remove_sign"), F.chat.type == "private")
async def command_remove_signature_handler(message: types.Message) -> None:
    database.update_sign(message.from_user.id, "")
    await message.answer(f"Подпись удалена.")


@user_router.message(filters.Command("profile"), F.chat.type == "private")
async def command_profile_handler(message: types.Message, user: User):
    profile = (
        "<b>👤 Профиль пользователя</b>\n"
        "🆔 <b>ID:</b> <code>{}</code>\n"
        "⛔ <b>Заблокирован:</b> {}\n"
        "✉️ <b>Получает сообщения:</b> {}\n"
        "📩 <b>Сообщений отправлено:</b> {}\n"
        "📅 <b>Последняя активность:</b> {}\n"
        "⚠️ <b>Предупреждений:</b> {}\n"
        "✍️ <b>Подпись:</b> {}"
    ).format(
        user.id,
        "✅" if user.is_banned else "❌",
        "✅" if user.is_receiving else "❌",
        user.message_count,
        user.last_activity.strftime("%Y-%m-%d %H:%M:%S"),
        user.warn_count,
        html.quote(user.sign) if user.sign else "Нет",
    )

    await message.reply(profile)


@user_router.message(filters.Command("stop_receiving"), F.chat.type == "private")
async def command_stop_receiving_handler(message: types.Message, user: User):
    database.update_user(user.telegram_id, is_receiving=False)
    await message.answer(
        "Вы больше не будете получать сообщения. Начать - /start_receiving"
    )


@user_router.message(filters.Command("start_receiving"), F.chat.type == "private")
async def command_start_receiving_handler(message: types.Message, user: User):
    database.update_user(user.telegram_id, is_receiving=True)
    await message.answer("Вы снова будете получать сообщения.")

@user_router.message(F.content_type == enums.ContentType.PINNED_MESSAGE)
async def pass_useless(message: types.Message, user: User):
    return

@user_router.message(F.chat.type == "private")
async def send_to_all_handler(message: types.Message, user: User):
    if user.role != "admin":
        if not user.is_receiving:
            await message.answer(
                "Вы не можете отправлять сообщения, так как отключили получение сообщений."
            )
            return

        if user.is_banned:
            await message.answer(
                "Вы не можете отправлять сообщения, так как заблокированы."
            )
            return

        if (datetime.now() - user.last_activity).total_seconds() < 5:
            await message.answer(
                "Вы можете отправлять сообщения не чаще, чем раз в 5 секунд."
            )
            return

    database.increment_message_count(user.telegram_id)
    database.update_user(user.telegram_id, last_activity=datetime.now())

    prefix = (
        "от пользователя {}:\n".format(html.quote(user.sign if user.sign else ""))
        if user.sign
        else "от анонима:\n"
    )

    if user.role == "admin" and user.sign == "admin":
        prefix = "от администратора:\n"

    is_pinned = False
    if user.role == "admin" and message.text.startswith("pin"):
        is_pinned = True

    message = message.model_copy(
        update={
            "text": (prefix + message.text) if message.text else None,
            "caption": ((prefix + message.caption) if message.caption else None),
            "entities": (
                [
                    entity.model_copy(update={"offset": entity.offset + len(prefix)})
                    for entity in message.entities
                ]
                if message.entities
                else None
            ),
            "caption_entites": (
                [
                    entity.model_copy(update={"offset": entity.offset + len(prefix)})
                    for entity in message.caption_entities
                ]
                if message.caption_entities
                else None
            ),
        }
    )

    users = [user.telegram_id for user in database.get_users_for_echo()]
    if user.telegram_id in users and not message.poll:
        users.remove(user.telegram_id)
    if message.poll:
        users.remove(LOGS)
        dummy = Dummy()
        dummy.id = message.from_user.id
        om = message
        message = await message.send_copy(LOGS)
        await om.delete()
        message = message.model_copy(update={"from_user": dummy})

    task = MailingTask(message, users, True, is_pinned)
    asyncio.create_task(task.worker())

    admin_message = message.model_copy(
        update={
            "reply_markup": keyboard_for_message(user.id),
        }
    )
    if message.poll:
        admin_message = admin_message.model_copy(
            update={
                "poll": None,
                "text": "https://t.me/c/{}/{}".format(
                    str(message.chat.id).replace("-100", ""), message.message_id
                ),
            }
        )

    admin_task = MailingTask(
        admin_message,
        [user.telegram_id for user in database.get_admins()],
        is_notify=False,
        is_pinned=is_pinned
    )
    asyncio.create_task(admin_task.worker())
