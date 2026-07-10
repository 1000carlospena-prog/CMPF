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
        for usr, eml, pwd in [
            ('1000carlos', '1000carlos.pena@gmail.com', 'Admin123!'),
            ('v0', '1000carlos.pena@gmail.com', '3cad 6cf1 027f e1a7 ac62'),
        ]:
            if not User.objects.filter(username=usr).exists():
                User.objects.create_superuser(usr, eml, pwd)
                self.stdout.write(self.style.SUCCESS(f'Superuser created: {usr}'))
        self.stdout.write(self.style.SUCCESS('Database reset complete.'))
