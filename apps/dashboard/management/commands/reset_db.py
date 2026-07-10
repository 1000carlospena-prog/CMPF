from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from apps.usuarios.models import Profile


class Command(BaseCommand):
    help = 'Resets database, runs migrations, creates superusers'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)

        user = User.objects.create_superuser('v00', '1000carlos.pena@gmail.com', '3cad 6cf1 027f e1a7 ac62')
        user.profile.grado = 'v00'
        user.profile.save()
        self.stdout.write(self.style.SUCCESS('Creado: v00 (Desarrollador)'))

        user = User.objects.create_superuser('1000carlos', '1000carlos.pena@gmail.com', 'Carlos1*')
        user.profile.grado = 'v1'
        user.profile.save()
        self.stdout.write(self.style.SUCCESS('Creado: 1000carlos (Super Admin)'))

        self.stdout.write(self.style.SUCCESS('Database reset complete.'))
