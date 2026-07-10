from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Carga datos iniciales solo si la base está vacía'

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write('La base de datos ya tiene usuarios. Omitiendo carga inicial.')
            return
        self.stdout.write('Base vacía. Cargando data.json...')
        call_command('loaddata', 'data.json', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Datos cargados correctamente.'))
