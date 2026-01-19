from django.contrib import admin
from .models import GitHubWebhook


@admin.register(GitHubWebhook)
class GitHubWebhookAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('event_type',)
    readonly_fields = ('payload', 'signature', 'created_at', 'updated_at')
    ordering = ('-created_at',)
