"""
Telegram Bot — отслеживает посты по хэштегу в группе.
Сохраняет статистику в базу данных Django (через ORM напрямую).
"""

import asyncio
import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Настройка путей для Django ORM
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "web"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tgstat_project.settings")
django.setup()

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Filter

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONITOR_CHAT_ID = os.getenv("MONITOR_CHAT_ID", "")
TRACK_HASHTAG = os.getenv("TRACK_HASHTAG", "news").lower().strip("#")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле!")

# Импорт моделей ПОСЛЕ django.setup()
from dashboard.models import Post, TrackedChat


class HashtagFilter(Filter):
    """Фильтр сообщений по хэштегу."""

    def __init__(self, hashtag: str):
        self.hashtag = f"#{hashtag.lower()}"

    async def __call__(self, message: Message) -> bool:
        text = message.text or message.caption or ""
        return self.hashtag in text.lower()


class ChatFilter(Filter):
    """Фильтр: только из отслеживаемого чата."""

    async def __call__(self, message: Message) -> bool:
        if not MONITOR_CHAT_ID:
            return True  # если не задан — слушаем все чаты
        chat = message.chat
        return str(chat.id) == str(MONITOR_CHAT_ID) or chat.username == MONITOR_CHAT_ID.lstrip("@")


def get_author_info(message: Message) -> tuple[str, str | None]:
    """Извлекает имя и username автора поста."""
    user = message.from_user
    if user:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "Неизвестно"
        username = f"@{user.username}" if user.username else None
        return name, username

    # Для анонимных постов от имени канала
    if message.sender_chat:
        return message.sender_chat.title or "Канал", None

    return "Неизвестно", None


async def save_post(message: Message, hashtag: str):
    """Сохраняет пост в базу данных."""
    author_name, author_username = get_author_info(message)
    text = message.text or message.caption or ""
    chat = message.chat

    # Убеждаемся, что чат есть в базе
    tracked_chat, _ = TrackedChat.objects.get_or_create(
        chat_id=str(chat.id),
        defaults={
            "title": chat.title or chat.username or str(chat.id),
            "username": chat.username,
        },
    )

    Post.objects.create(
        message_id=message.message_id,
        chat=tracked_chat,
        hashtag=hashtag,
        text=text[:4000],  # ограничение поля
        author_name=author_name,
        author_username=author_username or "",
        author_id=str(message.from_user.id) if message.from_user else "",
        posted_at=message.date or datetime.utcnow(),
    )

    print(f"[✓] Сохранён пост #{hashtag} от {author_name} в чате «{chat.title}»")


def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    hashtag_filter = HashtagFilter(TRACK_HASHTAG)
    chat_filter = ChatFilter()

    @dp.message(chat_filter, hashtag_filter)
    async def handle_tagged_message(message: Message):
        await save_post(message, TRACK_HASHTAG)

    # Также слушаем посты-каналы (channel_post)
    @dp.channel_post(hashtag_filter)
    async def handle_channel_post(message: Message):
        await save_post(message, TRACK_HASHTAG)

    print(f"🤖 Бот запущен. Отслеживаю хэштег: #{TRACK_HASHTAG}")
    if MONITOR_CHAT_ID:
        print(f"📍 Чат: {MONITOR_CHAT_ID}")
    else:
        print("📍 Чат: все доступные чаты")

    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
