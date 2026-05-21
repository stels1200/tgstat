import json
from datetime import timedelta, date

from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncHour
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import Post, TrackedChat


def dashboard(request):
    """Главная страница дашборда."""
    # Фильтры из GET-параметров
    hashtag_filter = request.GET.get("hashtag", "")
    chat_filter = request.GET.get("chat", "")
    days = int(request.GET.get("days", 30))

    since = timezone.now() - timedelta(days=days)

    qs = Post.objects.filter(posted_at__gte=since)
    if hashtag_filter:
        qs = qs.filter(hashtag__icontains=hashtag_filter)
    if chat_filter:
        qs = qs.filter(chat_id=chat_filter)

    # Общая статистика
    total_posts = qs.count()
    unique_authors = qs.exclude(author_id="").values("author_id").distinct().count()

    # Топ-авторы
    top_authors = (
        qs.exclude(author_name="")
        .values("author_name", "author_username")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Посты по дням (для графика)
    posts_by_day = (
        qs.annotate(day=TruncDate("posted_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    # Посты по хэштегам
    posts_by_hashtag = (
        qs.values("hashtag")
        .annotate(count=Count("id"))
        .order_by("-count")[:15]
    )

    # Активность по часам
    posts_by_hour = (
        qs.annotate(hour=TruncHour("posted_at"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )

    # Последние посты
    recent_posts = qs.select_related("chat").order_by("-posted_at")[:50]

    # Данные для фильтров
    all_hashtags = (
        Post.objects.values_list("hashtag", flat=True).distinct().order_by("hashtag")
    )
    all_chats = TrackedChat.objects.all()

    # Активность по часам (0-23)
    hour_buckets = [0] * 24
    for entry in posts_by_hour:
        h = entry["hour"].hour if entry["hour"] else 0
        hour_buckets[h] += entry["count"]

    # Данные для JS-графиков (JSON)
    chart_days = [str(e["day"]) for e in posts_by_day]
    chart_counts = [e["count"] for e in posts_by_day]

    context = {
        "total_posts": total_posts,
        "unique_authors": unique_authors,
        "top_authors": top_authors,
        "recent_posts": recent_posts,
        "posts_by_hashtag": posts_by_hashtag,
        "all_hashtags": list(all_hashtags),
        "all_chats": all_chats,
        "chart_days_json": json.dumps(chart_days),
        "chart_counts_json": json.dumps(chart_counts),
        "hour_buckets_json": json.dumps(hour_buckets),
        # Активные фильтры
        "active_hashtag": hashtag_filter,
        "active_chat": chat_filter,
        "active_days": days,
    }
    return render(request, "dashboard/index.html", context)


@require_GET
def api_stats(request):
    """API-эндпоинт для получения статистики в JSON (для AJAX-обновления)."""
    days = int(request.GET.get("days", 7))
    since = timezone.now() - timedelta(days=days)

    qs = Post.objects.filter(posted_at__gte=since)

    posts_by_day = list(
        qs.annotate(day=TruncDate("posted_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    return JsonResponse(
        {
            "total": qs.count(),
            "by_day": [
                {"date": str(e["day"]), "count": e["count"]} for e in posts_by_day
            ],
        }
    )
