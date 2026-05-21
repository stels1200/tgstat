from django.contrib import admin
from .models import Post, TrackedChat


@admin.register(TrackedChat)
class TrackedChatAdmin(admin.ModelAdmin):
    list_display = ["title", "chat_id", "username", "added_at"]
    search_fields = ["title", "chat_id", "username"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["hashtag", "author_name", "chat", "posted_at", "short_text"]
    list_filter = ["hashtag", "chat", "posted_at"]
    search_fields = ["author_name", "author_username", "text", "hashtag"]
    date_hierarchy = "posted_at"
    ordering = ["-posted_at"]

    def short_text(self, obj):
        return obj.text[:80] + "..." if len(obj.text) > 80 else obj.text
    short_text.short_description = "Текст"
