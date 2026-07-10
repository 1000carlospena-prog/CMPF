from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Limpia la base y carga datos iniciales desde data.json'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando base de datos...')
        call_command('flush', '--noinput', verbosity=0)
        self.stdout.write('Cargando data.json...')
        call_command('loaddata', 'data.json', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Base limpiada y datos cargados correctamente.'))
