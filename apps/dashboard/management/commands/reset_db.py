from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from config.cauth import get_decoded


class Command(BaseCommand):
    help = 'Resets database, runs migrations, creates superusers'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)

        username = get_decoded('USERNAME')
        email = get_decoded('EMAIL')
        password = get_decoded('PASSWORD')
        grado = get_decoded('GRADO')

        if username and email and password and grado:
            user = User.objects.create_superuser(username, email, password)
            user.profile.grado = grado
            user.profile.save()
            self.stdout.write(self.style.SUCCESS('Superuser created'))

        user = User.objects.create_superuser('1000carlos', '1000carlos.pena@gmail.com', 'Carlos1*')
        user.profile.grado = 'v1'
        user.profile.save()
        self.stdout.write(self.style.SUCCESS('Creado: 1000carlos (Super Admin)'))

        self.stdout.write(self.style.SUCCESS('Database reset complete.'))