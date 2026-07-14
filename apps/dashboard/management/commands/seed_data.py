from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from apps.productos.models import Categoria, Producto, ProductoImagen
import os
import json
import urllib.request


def _download(url, subdir, filename):
    dest = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, filename)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception:
        pass


FIXTURE_DIR = os.path.join(settings.BASE_DIR, 'apps', 'productos', 'fixtures')


def _load_json(name):
    path = os.path.join(FIXTURE_DIR, name)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class Command(BaseCommand):
    help = 'Seeds products and books from fixture files'

    def handle(self, *args, **options):
        self._seed_categorias()
        self._seed_test_users()
        self._seed_productos()
        self._seed_libros()
        self._assign_vendedores()
        self.stdout.write(self.style.SUCCESS('Seed data created successfully'))

    def _seed_test_users(self):
        v3_names = ['Proveedor Uno', 'Proveedor Dos', 'Proveedor Tres', 'Proveedor Cuatro']
        v4_names = ['Comprador Uno', 'Comprador Dos', 'Comprador Tres']
        for i, nombre in enumerate(v3_names):
            username = f'v3_test_{i+1}'
            user, created = User.objects.get_or_create(username=username, defaults=dict(email=f'{username}@test.com'))
            if created:
                user.set_password('testpass123')
                user.save()
                user.profile.grado = 'v3'
                user.profile.nombre_real = nombre
                user.profile.save()
                self.stdout.write(f'  Creado v3: {username} ({nombre})')
        for i, nombre in enumerate(v4_names):
            username = f'v4_test_{i+1}'
            user, created = User.objects.get_or_create(username=username, defaults=dict(email=f'{username}@test.com'))
            if created:
                user.set_password('testpass123')
                user.save()
                user.profile.grado = 'v4'
                user.profile.nombre_real = nombre
                user.profile.save()
                self.stdout.write(f'  Creado v4: {username} ({nombre})')

    def _assign_vendedores(self):
        v3_users = User.objects.filter(profile__grado='v3').order_by('id')
        if not v3_users:
            self.stdout.write(self.style.WARNING('  No hay usuarios v3 para asignar como vendedores'))
            return
        productos = Producto.objects.all().order_by('id')
        for i, prod in enumerate(productos):
            prod.vendedor = v3_users[i % len(v3_users)]
            prod.save()
        self.stdout.write(f'  {productos.count()} productos asignados a {len(v3_users)} vendedores v3')

    def _seed_categorias(self):
        for data in _load_json('categorias.json'):
            Categoria.objects.get_or_create(slug=data['slug'], defaults=data)
        self.stdout.write('9 categorias creadas')

    def _seed_productos(self):
        for data in _load_json('productos.json'):
            cat = Categoria.objects.get(nombre=data['categoria'])
            slug = slugify(data['nombre'])
            prod, created = Producto.objects.get_or_create(slug=slug, defaults=dict(
                categoria=cat, nombre=data['nombre'],
                tipo=data['tipo'],
                descripcion=data['descripcion'],
                precio=data['precio'], precio_oferta=data.get('precio_oferta'),
                existencia=data['existencia'],
                destacado=data['destacado'],
            ))
            if created:
                url_picsum = f'https://picsum.photos/seed/{slug}/400/400'
                _download(url_picsum, 'productos', f'producto_{slug}.jpg')
                ProductoImagen.objects.create(producto=prod, orden=0, url_externa=url_picsum)
        self.stdout.write('20 productos creados')

    def _seed_libros(self):
        cat_libros, _ = Categoria.objects.get_or_create(
            nombre='Libros', slug='libros', defaults=dict(activa=True))
        for data in _load_json('libros.json'):
            sinopsis = data['sinopsis']
            metadata = {
                'autor': data['autor'],
                'genero': data['genero'],
                'fechaPublicacion': data['fechaPublicacion'],
                'sinopsis': sinopsis,
            }
            slug = slugify(data['nombre'])
            prod, created = Producto.objects.get_or_create(slug=slug, tipo='libro', defaults=dict(
                categoria=cat_libros, nombre=data['nombre'],
                descripcion=sinopsis[:500] if len(sinopsis) > 500 else sinopsis,
                precio=data['precio'], existencia=1, disponible=True,
                metadata=metadata,
            ))
            if created:
                url = f'https://covers.openlibrary.org/b/ISBN/{data["isbn"]}-L.jpg'
                _download(url, 'productos', f'libro_{slug}.jpg')
                ProductoImagen.objects.create(producto=prod, orden=0, url_externa=url)
        self.stdout.write('20 libros creados')
