from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from config.v00_auth import get_decoded


class Command(BaseCommand):
    help = 'Deletes all users and creates fresh superusers'

    def handle(self, *args, **options):
        self.stdout.write('Eliminando todos los usuarios...')
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los usuarios eliminados.'))

        username = get_decoded('USERNAME')
        email = get_decoded('EMAIL')
        password = get_decoded('PASSWORD')
        grado = get_decoded('GRADO')

        if username and email and password and grado:
            User.objects.create_superuser(username, email, password)
            p = User.objects.get(username=username).profile
            p.grado = grado
            p.save()
            self.stdout.write(self.style.SUCCESS('Superuser created'))

        User.objects.create_superuser('1000carlos', '1000carlos.pena@gmail.com', 'Carlos1*')
        p = User.objects.get(username='1000carlos').profile
        p.grado = 'v1'
        p.save()
        self.stdout.write(self.style.SUCCESS('Creado: 1000carlos (Super Admin)'))

        self.stdout.write(self.style.SUCCESS('Completado.'))