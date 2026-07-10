from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Lists all registered users and their grades'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('date_joined')
        if not users:
            self.stdout.write('No hay usuarios registrados.')
            return
        self.stdout.write(f'{len(users)} usuarios registrados:')
        self.stdout.write('')
        self.stdout.write(f'{"ID":<5} {"Usuario":<20} {"Email":<35} {"Grado":<8} {"Staff":<6} {"Superuser":<10}')
        self.stdout.write('-' * 84)
        for u in users:
            grado = getattr(u.profile, 'grado', '-')
            self.stdout.write(f'{u.id:<5} {u.username:<20} {u.email:<35} {grado:<8} {str(u.is_staff):<6} {str(u.is_superuser):<10}')