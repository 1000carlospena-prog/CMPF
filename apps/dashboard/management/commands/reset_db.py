from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Resets database, runs migrations, creates superuser'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)
        if not User.objects.filter(username='1000carlos').exists():
            User.objects.create_superuser('1000carlos', '1000carlos.pena@gmail.com', 'Admin123!')
            self.stdout.write(self.style.SUCCESS('Superuser created: 1000carlos / Admin123!'))
        self.stdout.write(self.style.SUCCESS('Database reset complete.'))
