from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Resets database and runs migrations from scratch'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Database reset complete.'))
