from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f"Conversation {self.id} ({self.participants.count()} participants)"

    @property
    def last_message(self):
        return self.messages.order_by('-created').first()

    @property
    def other_users(self, user):
        return self.participants.exclude(id=user.id)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
