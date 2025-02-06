from aiogram import types

main_admin_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Рассылка")],
        [types.KeyboardButton(text="Статистика")],
        [types.KeyboardButton(text="Дамп")],
    ],
    resize_keyboard=True,
)

approve_mailing_inline = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="🔥Уверен", callback_data="mailing_approve")],
        [types.InlineKeyboardButton(text="🟥Отмена", callback_data="mailing_cancel")],
    ]
)


def keyboard_for_message(user_id: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(text="Warn", callback_data=f"warn_{user_id}"),
            types.InlineKeyboardButton(text="Ban", callback_data=f"ban_{user_id}"),
        ]]
    )
