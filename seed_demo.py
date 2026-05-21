"""
Скрипт для заполнения базы тестовыми данными.
Запускать из папки web/:  python manage.py shell < ../seed_demo.py
Или напрямую:             python seed_demo.py
"""

import os
import sys
import django
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
import random

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "web"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tgstat_project.settings")
django.setup()

from dashboard.models import Post, TrackedChat

# Тестовые чаты
chats_data = [
    {"chat_id": "-1001111111111", "title": "Python Developers RU", "username": "pythondevru"},
    {"chat_id": "-1002222222222", "title": "Django Community", "username": "djangocommunity"},
]

authors = [
    ("Алексей Смирнов", "@alex_dev", "111001"),
    ("Мария Иванова", "@maria_codes", "111002"),
    ("Дмитрий Козлов", "@dima_k", "111003"),
    ("Анна Петрова", "@anna_p", "111004"),
    ("Сергей Новиков", "@serg_n", "111005"),
    ("Ольга Зайцева", "@olga_z", "111006"),
]

hashtags = ["news", "python", "django", "aiogram", "tutorial", "release", "question"]

sample_texts = [
    "Вышла новая версия библиотеки. #{tag} Советую обновиться — много фиксов.",
    "Написал статью о том, как настроить деплой на VPS. #{tag} Ссылка в закрепе.",
    "#{tag} Кто сталкивался с этой ошибкой? Не могу понять в чём проблема.",
    "#{tag} Анонс митапа в эту субботу! Будем разбирать архитектуру async-приложений.",
    "Полезный туториал по async/await в Python. #{tag} Рекомендую всем новичкам.",
    "#{tag} Обновил пакет до v2.0 — ломающие изменения, читайте changelog!",
    "Небольшой лайфхак при работе с Django ORM. #{tag} Сэкономил пару часов.",
]

print("Создаём тестовые чаты...")
chats = []
for data in chats_data:
    chat, created = TrackedChat.objects.get_or_create(
        chat_id=data["chat_id"],
        defaults={"title": data["title"], "username": data["username"]},
    )
    chats.append(chat)
    print(f"  {'✓ создан' if created else '· уже есть'}: {chat.title}")

print("\nГенерируем посты за последние 30 дней...")
now = timezone.now()
count = 0

for i in range(120):
    tag = random.choice(hashtags)
    author_name, author_username, author_id = random.choice(authors)
    chat = random.choice(chats)
    text_template = random.choice(sample_texts)
    text = text_template.replace("{tag}", tag)

    days_back = random.randint(0, 30)
    hours_back = random.randint(0, 23)
    posted_at = now - timedelta(days=days_back, hours=hours_back, minutes=random.randint(0, 59))

    try:
        Post.objects.create(
            message_id=100000 + i,
            chat=chat,
            hashtag=tag,
            text=text,
            author_name=author_name,
            author_username=author_username,
            author_id=author_id,
            posted_at=posted_at,
        )
        count += 1
    except Exception:
        pass  # уже существует

print(f"\n✅ Создано {count} тестовых постов!")
print("Запустите Django-сервер: cd web && python manage.py runserver")
