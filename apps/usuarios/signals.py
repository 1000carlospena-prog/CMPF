from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
