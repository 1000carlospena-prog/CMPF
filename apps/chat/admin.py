from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'created']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'updated', 'participant_list']
    inlines = [MessageInline]

    def participant_list(self, obj):
        return ", ".join(p.username for p in obj.participants.all())


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'short_content', 'created', 'read']
    list_filter = ['read', 'created']

    def short_content(self, obj):
        return obj.content[:60]
