from aiogram import Router, filters, types, F, Bot
from telegram.middlewares.user import UserMiddleware
from db.models import User
from db import database
from telegram.keyboards.admin import main_admin_menu
from telegram.routes.admin.mailing.router import mailing_router
from db import methods

admin_router = Router(name=__name__)
admin_router.message.middleware(UserMiddleware())
admin_router.callback_query.middleware(UserMiddleware())
admin_router.include_router(mailing_router)


@admin_router.message(filters.Command("admin"))
async def command_admin_handler(message: types.Message, user: User) -> None:
    if user.role != "admin":
        return

    await message.answer(
        "Панель администратора открыта!",
        reply_markup=main_admin_menu,
    )

@admin_router.message(filters.Command("hide_buttons_please"))
async def hide_buttons_please(message: types.Message, user: User) -> None:
    await message.answer(
        "success",
        reply_markup=types.ReplyKeyboardRemove(),
    )

@admin_router.message(F.text == "Статистика")
async def admin(message: types.Message, user: User) -> None:
    if user.role != "admin":
        return

    stats = database.count_users()

    await message.answer(
        "Всего пользователей: {}\n"
        "Живых пользователей: {}\n"
        "Мертвых пользователей: {}\n".format(
            stats["total_users"],
            stats["receiving_messages_users"],
            stats["banned_bot_users"]
        )
    )


@admin_router.message(filters.Command("promote"))
async def promote(message: types.Message, user: User) -> None:
    if user.role != "admin":
        return

    args = message.text.split(" ")
    try:
        admin_id = int(args[1])
    except:
        await message.answer("Невреный ID (Не число)")
    if admin_id == user.id:
        await message.answer("Запрещено использовать эту команду на себя")
    database.update_user(admin_id, role="admin")
    await message.answer(
        "Пользователь с id {} назначен администратором".format(admin_id)
    )


@admin_router.message(filters.Command("demote"))
async def demote(message: types.Message, user: User) -> None:
    if user.role != "admin":
        return

    args = message.text.split(" ")
    try:
        admin_id = int(args[1])
    except:
        await message.answer("Невреный ID (Не число)")
    if admin_id == user.id:
        await message.answer("Запрещено использовать эту команду на себя")
    database.update_user(admin_id, role="user")
    await message.answer(
        "Пользователь с id {} больше не является администратором".format(admin_id)
    )


@admin_router.message(F.text == "Дамп")
async def admin(message: types.Message, user: User, bot: Bot) -> None:
    if user.role != "admin":
        return

    await bot.send_document(
        message.from_user.id,
        types.FSInputFile("db.db"),
    )

@admin_router.callback_query(F.data.startswith("warn_"))
async def warn_user(call: types.CallbackQuery, user: User) -> None:
    if user.role != "admin":
        return
    target_user_id = call.data.split("_")[1]
    database.add_warn(target_user_id)
    user = database.get_user_by_id(target_user_id)
    await call.message.reply(f"Пользователь с ID {target_user_id} получил предупреждение.")
    await call.bot.send_message(
        user.telegram_id, "Вы получили предупреждение от администратора."
    )
    await call.answer("ok")

@admin_router.callback_query(F.data.startswith("ban_"))
async def ban_user(call: types.CallbackQuery, user: User) -> None:
    if user.role != "admin":
        return
    target_user_id = call.data.split("_")[1]
    database.ban_user(target_user_id)
    user = database.get_user_by_id(target_user_id)
    await call.message.reply(f"Пользователь с ID {target_user_id} был забанен.")
    await call.bot.send_message(
        user.telegram_id, "Вы были забанены администратором."
    )
    await call.answer("ok")
