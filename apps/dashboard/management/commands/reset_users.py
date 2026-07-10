from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.usuarios.models import Profile


class Command(BaseCommand):
    help = 'Deletes all users and creates v00 + 1000carlos(v1)'

    def handle(self, *args, **options):
        self.stdout.write('Eliminando todos los usuarios...')
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los usuarios eliminados.'))

        User.objects.create_superuser('v00', '1000carlos.pena@gmail.com', '3cad 6cf1 027f e1a7 ac62')
        p = Profile.objects.get(user__username='v00')
        p.grado = 'v00'
        p.save()
        self.stdout.write(self.style.SUCCESS('Creado: v00 (Desarrollador)'))

        User.objects.create_superuser('1000carlos', '1000carlos.pena@gmail.com', 'Carlos1*')
        p = Profile.objects.get(user__username='1000carlos')
        p.grado = 'v1'
        p.save()
        self.stdout.write(self.style.SUCCESS('Creado: 1000carlos (Super Admin)'))

        self.stdout.write(self.style.SUCCESS('Completado.'))
