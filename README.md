# TG·STAT — Telegram Post Tracker

Бот отслеживает посты в Telegram-группах/каналах по заданному хэштегу и показывает статистику в веб-интерфейсе на Django.

---

## Структура проекта

```
tgstat/
├── bot/
│   └── bot.py            # Telegram-бот (aiogram 3)
├── web/
│   ├── manage.py
│   ├── tgstat_project/
│   │   ├── settings.py
│   │   └── urls.py
│   └── dashboard/
│       ├── models.py     # Post, TrackedChat
│       ├── views.py      # Дашборд + JSON API
│       ├── urls.py
│       ├── admin.py
│       └── templates/
│           └── dashboard/
│               └── index.html
├── seed_demo.py          # Тестовые данные
├── requirements.txt
└── .env.example
```

---

## Быстрый старт

### 1. Клонируйте и установите зависимости

```bash
cd tgstat
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройте переменные окружения

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
# Токен вашего бота (получить у @BotFather)
BOT_TOKEN=1234567890:ABCDEF...

# ID или @username чата для мониторинга
# Для группы: -1001234567890
# Для канала: @mychannel
MONITOR_CHAT_ID=@your_group

# Хэштег для отслеживания (без #)
TRACK_HASHTAG=news

# Django
SECRET_KEY=your-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Создайте базу данных

```bash
cd web
python manage.py migrate
python manage.py createsuperuser   # для доступа к /admin/
```

### 4. (Опционально) Загрузите тестовые данные

```bash
cd ..     # вернитесь в корень проекта tgstat/
python seed_demo.py
```

### 5. Запустите Django-сервер

```bash
cd web
python manage.py runserver
```

Откройте: **http://127.0.0.1:8000**

### 6. Запустите бота (в отдельном терминале)

```bash
cd tgstat/    # корень проекта
python bot/bot.py
```

---

## Как добавить бота в группу

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Добавьте бота в вашу группу/канал как **администратора**
3. Дайте права **«Читать сообщения»**
4. Для приватных групп получите ID: отправьте любое сообщение, затем используйте `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

## Возможности дашборда

| Раздел | Описание |
|--------|----------|
| **KPI-карточки** | Общее число постов, авторов, тегов, чатов |
| **График по дням** | Активность публикаций за выбранный период |
| **График по часам** | В какое время суток чаще всего постят |
| **Топ авторов** | Кто публикует больше всего (опционально) |
| **Хэштеги** | Распределение по тегам |
| **Лента постов** | Последние 50 постов с фильтрацией |
| **Фильтры** | По хэштегу, чату, периоду |

Страница **автоматически обновляется каждые 60 секунд**.

---

## Отслеживание нескольких хэштегов

Чтобы отслеживать несколько тегов, запустите несколько экземпляров бота с разными `.env`:

```bash
TRACK_HASHTAG=news python bot/bot.py &
TRACK_HASHTAG=release python bot/bot.py &
```

Или измените `bot.py`: добавьте список тегов в `TRACK_HASHTAG` через запятую и обновите `HashtagFilter`.

---

## JSON API

`GET /api/stats/?days=7` — статистика за N дней в формате JSON:

```json
{
  "total": 42,
  "by_day": [
    {"date": "2024-01-15", "count": 8},
    ...
  ]
}
```

---

## Технологии

- **aiogram 3** — асинхронный фреймворк для Telegram Bot API
- **Django 5** — веб-фреймворк для дашборда
- **SQLite** — база данных (можно заменить на PostgreSQL)
- **Chart.js** — графики в браузере
- **WhiteNoise** — раздача статики
