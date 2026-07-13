from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from apps.productos.models import Categoria, Producto, ProductoImagen
from datetime import date
import os
import urllib.request


def _download(url, filename):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    path = os.path.join(settings.MEDIA_ROOT, filename)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception:
        pass


class Command(BaseCommand):
    help = 'Seeds 20 products and 20 books'

    def handle(self, *args, **options):
        self._seed_categorias()
        self._seed_productos()
        self._seed_libros()
        self.stdout.write(self.style.SUCCESS('Seed data created successfully'))

    def _seed_categorias(self):
        for nombre in ['Electrónica', 'Ropa y Accesorios', 'Hogar', 'Deportes',
                        'Juguetes', 'Salud y Belleza', 'Automotriz', 'Mascotas', 'Libros']:
            Categoria.objects.get_or_create(nombre=nombre, slug=slugify(nombre))
        self.stdout.write('9 categorias creadas')

    _TIPO_POR_CATEGORIA = {
        'Electrónica': 'digital',
        'Ropa y Accesorios': 'general',
        'Hogar': 'domestico',
        'Deportes': 'general',
        'Juguetes': 'general',
        'Salud y Belleza': 'general',
        'Automotriz': 'vehiculo',
        'Mascotas': 'domestico',
    }

    def _seed_productos(self):
        vendedor = User.objects.filter(is_superuser=True).first()
        data = [
            ('Audífonos Bluetooth', 'Electrónica', 29.99, 24.99, 50, True),
            ('Cargador USB-C 65W', 'Electrónica', 19.99, None, 100, True),
            ('Camiseta Algodón', 'Ropa y Accesorios', 14.99, 9.99, 80, True),
            ('Mochila Impermeable', 'Ropa y Accesorios', 39.99, None, 30, True),
            ('Lámpara LED Escritorio', 'Hogar', 34.99, 29.99, 45, True),
            ('Set Sartenes Antiadherentes', 'Hogar', 49.99, None, 20, False),
            ('Balón Fútbol', 'Deportes', 24.99, 19.99, 60, True),
            ('Pesa Rusa 16kg', 'Deportes', 44.99, None, 25, True),
            ('Rompecabezas 1000 piezas', 'Juguetes', 18.99, 14.99, 90, True),
            ('Muñeca Articulada', 'Juguetes', 22.99, None, 40, True),
            ('Crema Hidratante Facial', 'Salud y Belleza', 15.99, 12.99, 70, True),
            ('Set Cepillos Maquillaje', 'Salud y Belleza', 12.99, None, 55, False),
            ('Organizador Automotriz', 'Automotriz', 16.99, 13.99, 35, True),
            ('Limpiador Aire Acondicionado', 'Automotriz', 8.99, None, 65, True),
            ('Cama Perro Mediana', 'Mascotas', 32.99, 27.99, 15, True),
            ('Juguete Interactivo Gato', 'Mascotas', 11.99, None, 50, True),
            ('Reloj Inteligente', 'Electrónica', 89.99, 69.99, 10, True),
            ('Pantalón Deportivo', 'Ropa y Accesorios', 29.99, None, 35, False),
            ('Cojín Ergonómico', 'Hogar', 27.99, 22.99, 28, True),
            ('Raqueta Tenis', 'Deportes', 54.99, None, 12, True),
        ]
        for nombre, cat_nombre, precio, oferta, existencia, destacado in data:
            cat = Categoria.objects.get(nombre=cat_nombre)
            slug = slugify(nombre)
            prod, created = Producto.objects.get_or_create(slug=slug, defaults=dict(
                categoria=cat, nombre=nombre, vendedor=vendedor,
                tipo=self._TIPO_POR_CATEGORIA.get(cat_nombre, 'general'),
                descripcion=f'{nombre} de alta calidad al mejor precio.',
                precio=precio, precio_oferta=oferta, existencia=existencia,
                destacado=destacado,
            ))
            if created:
                url_picsum = f'https://picsum.photos/seed/{slug}/400/400'
                fname = f'producto_{slug}.jpg'
                _download(url_picsum, fname)
                ProductoImagen.objects.create(producto=prod, imagen=fname, url_externa=url_picsum, orden=0)
        self.stdout.write('20 productos creados')

    def _seed_libros(self):
        cat_libros = Categoria.objects.get_or_create(nombre='Libros', slug='libros', defaults=dict(activa=True))[0]
        isbns = [
            '9780307474728', '9780307387264', '9780061120084', '9780060926881',
            '9788437600444', '9788420633156', '9788420471846', '9788420471839',
            '9788437604572', '9788437603452', '9788437604244', '9789681600530',
            '9789681601407', '9788439704191', '9789562390655', '9789563140927',
            '9788437604169', '9788437604152', '9789681601070', '0811211959',
        ]

        libros = [
            ('Cien años de soledad', 'Gabriel García Márquez', 'Novela', 19.99, date(1967, 6, 5), 'La historia de la familia Buendía en Macondo.'),
            ('El amor en tiempos del cólera', 'Gabriel García Márquez', 'Novela', 17.99, date(1985, 9, 5), 'Una historia de amor que espera medio siglo.'),
            ('La casa de los espíritus', 'Isabel Allende', 'Novela', 16.99, date(1982, 1, 1), 'Saga familiar con elementos mágicos.'),
            ('Paula', 'Isabel Allende', 'Ensayo', 14.99, date(1994, 1, 1), 'Memorias dedicadas a su hija.'),
            ('Ficciones', 'Jorge Luis Borges', 'Cuento', 15.99, date(1944, 1, 1), 'Colección de cuentos fantásticos.'),
            ('El Aleph', 'Jorge Luis Borges', 'Cuento', 14.99, date(1949, 1, 1), 'Cuentos sobre infinito y laberintos.'),
            ('La ciudad y los perros', 'Mario Vargas Llosa', 'Novela', 16.99, date(1963, 1, 1), 'Vida en un colegio militar de Lima.'),
            ('Conversación en La Catedral', 'Mario Vargas Llosa', 'Novela', 18.99, date(1969, 1, 1), 'Retrato del Perú bajo el régimen de Odría.'),
            ('Rayuela', 'Julio Cortázar', 'Novela', 17.99, date(1963, 1, 1), 'Novela experimental y saltarina.'),
            ('Bestiario', 'Julio Cortázar', 'Cuento', 13.99, date(1951, 1, 1), 'Primera colección de cuentos de Cortázar.'),
            ('La muerte de Artemio Cruz', 'Carlos Fuentes', 'Novela', 15.99, date(1962, 1, 1), 'Vida de un revolucionario mexicano en su lecho de muerte.'),
            ('Aura', 'Carlos Fuentes', 'Novela', 12.99, date(1962, 1, 1), 'Novela corta de misterio y fantasía.'),
            ('Veinte poemas de amor', 'Pablo Neruda', 'Poesía', 11.99, date(1924, 1, 1), 'Poemario de amor juvenil.'),
            ('Confieso que he vivido', 'Pablo Neruda', 'Ensayo', 14.99, date(1974, 1, 1), 'Autobiografía del poeta.'),
            ('Desolación', 'Gabriela Mistral', 'Poesía', 12.99, date(1922, 1, 1), 'Primer gran poemario de Mistral.'),
            ('Tala', 'Gabriela Mistral', 'Poesía', 11.99, date(1938, 1, 1), 'Poemario que refleja la madurez poética.'),
            ('Pedro Páramo', 'Juan Rulfo', 'Novela', 13.99, date(1955, 1, 1), 'Novela sobre un pueblo fantasma.'),
            ('El llano en llamas', 'Juan Rulfo', 'Cuento', 12.99, date(1953, 1, 1), 'Cuentos de la Revolución Mexicana.'),
            ('El laberinto de la soledad', 'Octavio Paz', 'Ensayo', 14.99, date(1950, 1, 1), 'Ensayo sobre la identidad mexicana.'),
            ('Piedra de sol', 'Octavio Paz', 'Poesía', 10.99, date(1957, 1, 1), 'Poema extenso y emblemático.'),
        ]
        for i, (nombre, autor, genero, precio, fecha, sinopsis) in enumerate(libros):
            slug = slugify(nombre)
            metadata = {
                'autor': autor,
                'genero': genero,
                'fechaPublicacion': str(fecha),
                'sinopsis': sinopsis,
            }
            prod, created = Producto.objects.get_or_create(slug=slug, tipo='libro', defaults=dict(
                categoria=cat_libros, nombre=nombre,
                descripcion=sinopsis[:500] if len(sinopsis) > 500 else sinopsis,
                precio=precio, existencia=1, disponible=True,
                metadata=metadata,
            ))
            if created:
                fname = f'libro_{slug}.jpg'
                _download(f'https://covers.openlibrary.org/b/ISBN/{isbns[i]}-L.jpg', fname)
                ProductoImagen.objects.create(producto=prod, imagen=fname, orden=0,
                    url_externa=f'https://covers.openlibrary.org/b/ISBN/{isbns[i]}-L.jpg')
        self.stdout.write('20 libros creados')