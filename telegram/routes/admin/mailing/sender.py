import asyncio
import datetime
import time

from aiogram.types import ContentType, Message
from utils.telegram import bot
from logs.main import logger
from utils.constants import LOGS

SEND_METHODS = {
    ContentType.ANIMATION: "send_animation",
    ContentType.AUDIO: "send_audio",
    ContentType.DOCUMENT: "send_document",
    ContentType.PHOTO: "send_photo",
    ContentType.VIDEO: "send_video",
    ContentType.VIDEO_NOTE: "send_video_note",
    ContentType.STICKER: "send_sticker",
    ContentType.VOICE: "send_voice",
    "text": "send_message",
}


def get_file_id(message: Message):
    if not message.text:
        if message.document:
            return message.document.file_id
        elif message.photo:
            return message.photo[-1].file_id
        elif message.video:
            return message.video.file_id
        elif message.voice:
            return message.voice.file_id
        elif message.audio:
            return message.audio.file_id
        elif message.video_note:
            return message.video_note.file_id
        else:
            return message.animation.file_id
    return None


async def send_any_msg(msg, chat_id, markup=None):
    if msg.sticker:
        return await bot.send_sticker(
            chat_id=chat_id, sticker=msg.sticker.file_id, reply_markup=markup
        )

    text = msg.html_text

    if any(
        [
            msg.video,
            msg.animation,
            msg.photo,
            msg.video_note,
            msg.voice,
            msg.audio,
        ]
    ):
        media = get_file_id(msg)
        method = getattr(bot, SEND_METHODS[msg.content_type], None)

        if msg.video_note or msg.voice:
            return await method(chat_id, media, reply_markup=markup)
        else:
            return await method(
                chat_id, media, caption=text, reply_markup=markup, has_spoiler=False
            )

    if msg.dice:
        return await bot.send_dice(chat_id=chat_id)

    if msg.text:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup,
            disable_web_page_preview=True,
        )
    
    if msg.poll:
        return await msg.forward(chat_id=chat_id)

    raise ValueError("Неподдерживаемый тип поста")


class MailingTask:
    def __init__(self, message: Message, users: list[int], is_notify=True, is_pinned=False):
        self.users = users
        self.all_count = 0
        self.ban_count = 0
        self.last_second_count = 0
        self.message = message
        self.lock = asyncio.Lock()
        self.limit_per_sec = 24
        self.is_notify = is_notify
        self.current_second = (
            datetime.datetime.now().second
        ) 
        self.is_pinned = is_pinned

    async def send(self, user_id):
        """Функция отправки сообщения с обработкой ошибок"""
        try:
            message = await send_any_msg(self.message, user_id, markup=self.message.reply_markup)
            if self.is_pinned:
                await message.pin()
            async with self.lock:
                self.all_count += 1
        except Exception as e:
            async with self.lock:
                self.all_count += 1
                self.ban_count += 1
            logger.error(f"Ошибка при отправке пользователю {user_id}: {e}")

    async def worker(self):
        """Главный процесс рассылки"""
        start_time = time.time()

        if self.is_notify:
            notify = await bot.send_message(
                chat_id=self.message.from_user.id, text="Отправляю сообщение..."
            )

        for user_id in self.users:
            async with self.lock:
                now_second = datetime.datetime.now().second  # Берем текущее время

                # Если время поменялось, обнуляем счетчик
                if now_second != self.current_second:
                    self.last_second_count = 0
                    self.current_second = now_second

                # Если достигли лимита за секунду, ждем следующей секунды
                if self.last_second_count >= self.limit_per_sec:
                    while datetime.datetime.now().second == self.current_second:
                        await asyncio.sleep(0.1)  # Ждем смены секунды
                    self.last_second_count = 0
                    self.current_second = datetime.datetime.now().second

                self.last_second_count += 1

            # Ждем отправки перед продолжением (вместо create_task)
            await self.send(user_id)
            logger.info(f"Отправлено сообщение пользователю {user_id}")

        elapsed_time = time.time() - start_time
        if self.is_notify:
            await notify.edit_text(
                text=(
                    f"Сообщение отправлено {self.all_count - self.ban_count} пользователям за {elapsed_time:.2f} сек."
                ),
            )

        logger.info(
            f"Рассылка завершена. Получили рассылку: {self.all_count - self.ban_count}. "
            f"Заблокировали бота: {self.ban_count}. "
            f"Время рассылки: {elapsed_time:.2f} сек."
        )
