from django.test import TestCase
from django.contrib.auth.models import User
from apps.chat.models import Conversation, Message


class ChatModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')

    def test_crear_conversacion(self):
        conv = Conversation.objects.create()
        conv.participants.add(self.user1, self.user2)
        self.assertEqual(conv.participants.count(), 2)

    def test_enviar_mensaje(self):
        conv = Conversation.objects.create()
        conv.participants.add(self.user1, self.user2)
        msg = Message.objects.create(
            conversation=conv, sender=self.user1, content='Hola'
        )
        self.assertEqual(str(msg), 'user1: Hola')
        self.assertEqual(conv.last_message, msg)

    def test_mensaje_no_leido(self):
        conv = Conversation.objects.create()
        conv.participants.add(self.user1, self.user2)
        Message.objects.create(conversation=conv, sender=self.user1, content='Test')
        msg = conv.messages.first()
        self.assertFalse(msg.read)
