from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Lists all registered users and their roles'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('date_joined')
        if not users:
            self.stdout.write('No hay usuarios registrados.')
            return
        self.stdout.write(f'{len(users)} usuarios registrados:')
        self.stdout.write('')
        self.stdout.write(f'{"ID":<5} {"Usuario":<20} {"Email":<35} {"Rango":<15} {"Staff":<8} {"Superuser":<10}')
        self.stdout.write('-' * 93)
        for u in users:
            roles = []
            if u.is_superuser:
                roles.append('Superadmin')
            elif u.is_staff:
                roles.append('Staff')
            else:
                roles.append('Usuario')
            rango = ', '.join(roles)
            self.stdout.write(f'{u.id:<5} {u.username:<20} {u.email:<35} {rango:<15} {str(u.is_staff):<8} {str(u.is_superuser):<10}')
