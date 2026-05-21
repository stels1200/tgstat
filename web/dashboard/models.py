from django.db import models


class TrackedChat(models.Model):
    """Отслеживаемый Telegram-чат или группа."""

    chat_id = models.CharField(max_length=64, unique=True, verbose_name="ID чата")
    title = models.CharField(max_length=255, verbose_name="Название")
    username = models.CharField(max_length=128, blank=True, null=True, verbose_name="Username")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        ordering = ["title"]

    def __str__(self):
        return self.title or self.chat_id


class Post(models.Model):
    """Пост с отслеживаемым хэштегом."""

    message_id = models.BigIntegerField(verbose_name="ID сообщения")
    chat = models.ForeignKey(
        TrackedChat,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Чат",
    )
    hashtag = models.CharField(max_length=128, verbose_name="Хэштег", db_index=True)
    text = models.TextField(blank=True, verbose_name="Текст поста")
    author_name = models.CharField(max_length=255, blank=True, verbose_name="Имя автора")
    author_username = models.CharField(max_length=128, blank=True, verbose_name="Username автора")
    author_id = models.CharField(max_length=64, blank=True, verbose_name="ID автора")
    posted_at = models.DateTimeField(verbose_name="Время публикации", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Записан в БД")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-posted_at"]
        unique_together = [("message_id", "chat")]

    def __str__(self):
        return f"#{self.hashtag} от {self.author_name} [{self.posted_at:%d.%m.%Y %H:%M}]"

    @property
    def short_text(self):
        return self.text[:200] + "..." if len(self.text) > 200 else self.text
