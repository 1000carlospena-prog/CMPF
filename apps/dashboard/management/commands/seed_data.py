from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from apps.productos.models import Categoria, Producto, ProductoImagen
from apps.catalogo_libros.models import Autor, Editora, Generos, Libros
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
                        'Juguetes', 'Salud y Belleza', 'Automotriz', 'Mascotas']:
            Categoria.objects.get_or_create(nombre=nombre, slug=slugify(nombre))
        self.stdout.write('8 categorias creadas')

    def _seed_productos(self):
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
                categoria=cat, nombre=nombre,
                descripcion=f'{nombre} de alta calidad al mejor precio.',
                precio=precio, precio_oferta=oferta, existencia=existencia,
                destacado=destacado,
            ))
            if created:
                fname = f'producto_{slug}.jpg'
                _download(f'https://picsum.photos/seed/{slug}/400/400', fname)
                ProductoImagen.objects.create(producto=prod, imagen=fname, orden=0)
        self.stdout.write('20 productos creados')

    def _seed_libros(self):
        a1, _ = Autor.objects.get_or_create(nombre='Gabriel', apellido='García Márquez')
        a2, _ = Autor.objects.get_or_create(nombre='Isabel', apellido='Allende')
        a3, _ = Autor.objects.get_or_create(nombre='Jorge Luis', apellido='Borges')
        a4, _ = Autor.objects.get_or_create(nombre='Mario', apellido='Vargas Llosa')
        a5, _ = Autor.objects.get_or_create(nombre='Julio', apellido='Cortázar')
        a6, _ = Autor.objects.get_or_create(nombre='Carlos', apellido='Fuentes')
        a7, _ = Autor.objects.get_or_create(nombre='Pablo', apellido='Neruda')
        a8, _ = Autor.objects.get_or_create(nombre='Gabriela', apellido='Mistral')
        a9, _ = Autor.objects.get_or_create(nombre='Juan', apellido='Rulfo')
        a10, _ = Autor.objects.get_or_create(nombre='Octavio', apellido='Paz')

        e1, _ = Editora.objects.get_or_create(nombreEditora='Alfaguara', ciudad='Madrid')
        e2, _ = Editora.objects.get_or_create(nombreEditora='Planeta', ciudad='Barcelona')
        e3, _ = Editora.objects.get_or_create(nombreEditora='Anagrama', ciudad='Barcelona')
        e4, _ = Editora.objects.get_or_create(nombreEditora='Sudamericana', ciudad='Buenos Aires')
        e5, _ = Editora.objects.get_or_create(nombreEditora='Fondo Cultura', ciudad='Ciudad de México')

        gens = {}
        for g in ['Novela', 'Poesía', 'Cuento', 'Ensayo', 'Ficción']:
            gens[g], _ = Generos.objects.get_or_create(tipoGenero=g)

        isbns = [
            '9780307474728', '9780307387264', '9780061120084', '9780060926881',
            '9788437600444', '9788420633156', '9788420471846', '9788420471839',
            '9788437604572', '9788437603452', '9788437604244', '9789681600530',
            '9789681601407', '9788439704191', '9789562390655', '9789563140927',
            '9788437604169', '9788437604152', '9789681601070', '0811211959',
        ]

        libros = [
            ('Cien años de soledad', a1, gens['Novela'], e4, 19.99, date(1967, 6, 5), 'La historia de la familia Buendía en Macondo.'),
            ('El amor en tiempos del cólera', a1, gens['Novela'], e4, 17.99, date(1985, 9, 5), 'Una historia de amor que espera medio siglo.'),
            ('La casa de los espíritus', a2, gens['Novela'], e1, 16.99, date(1982, 1, 1), 'Saga familiar con elementos mágicos.'),
            ('Paula', a2, gens['Ensayo'], e1, 14.99, date(1994, 1, 1), 'Memorias dedicadas a su hija.'),
            ('Ficciones', a3, gens['Cuento'], e3, 15.99, date(1944, 1, 1), 'Colección de cuentos fantásticos.'),
            ('El Aleph', a3, gens['Cuento'], e3, 14.99, date(1949, 1, 1), 'Cuentos sobre infinito y laberintos.'),
            ('La ciudad y los perros', a4, gens['Novela'], e1, 16.99, date(1963, 1, 1), 'Vida en un colegio militar de Lima.'),
            ('Conversación en La Catedral', a4, gens['Novela'], e1, 18.99, date(1969, 1, 1), 'Retrato del Perú bajo el régimen de Odría.'),
            ('Rayuela', a5, gens['Novela'], e3, 17.99, date(1963, 1, 1), 'Novela experimental y saltarina.'),
            ('Bestiario', a5, gens['Cuento'], e3, 13.99, date(1951, 1, 1), 'Primera colección de cuentos de Cortázar.'),
            ('La muerte de Artemio Cruz', a6, gens['Novela'], e5, 15.99, date(1962, 1, 1), 'Vida de un revolucionario mexicano en su lecho de muerte.'),
            ('Aura', a6, gens['Novela'], e5, 12.99, date(1962, 1, 1), 'Novela corta de misterio y fantasía.'),
            ('Veinte poemas de amor', a7, gens['Poesía'], e4, 11.99, date(1924, 1, 1), 'Poemario de amor juvenil.'),
            ('Confieso que he vivido', a7, gens['Ensayo'], e4, 14.99, date(1974, 1, 1), 'Autobiografía del poeta.'),
            ('Desolación', a8, gens['Poesía'], e4, 12.99, date(1922, 1, 1), 'Primer gran poemario de Mistral.'),
            ('Tala', a8, gens['Poesía'], e4, 11.99, date(1938, 1, 1), 'Poemario que refleja la madurez poética.'),
            ('Pedro Páramo', a9, gens['Novela'], e5, 13.99, date(1955, 1, 1), 'Novela sobre un pueblo fantasma.'),
            ('El llano en llamas', a9, gens['Cuento'], e5, 12.99, date(1953, 1, 1), 'Cuentos de la Revolución Mexicana.'),
            ('El laberinto de la soledad', a10, gens['Ensayo'], e5, 14.99, date(1950, 1, 1), 'Ensayo sobre la identidad mexicana.'),
            ('Piedra de sol', a10, gens['Poesía'], e5, 10.99, date(1957, 1, 1), 'Poema extenso y emblemático.'),
        ]
        for i, (nombre, autor, genero, editora, precio, fecha, sinopsis) in enumerate(libros):
            slug = slugify(nombre)
            libro, created = Libros.objects.get_or_create(nombreLibro=nombre, defaults=dict(
                autor=autor, genero=genero, editora=editora, precio=precio,
                fechaPublicacion=fecha, sinopsis=sinopsis,
            ))
            if created:
                fname = f'libro_{slug}.jpg'
                _download(f'https://covers.openlibrary.org/b/ISBN/{isbns[i]}-L.jpg', fname)
                libro.imagen = fname
                libro.save()
        self.stdout.write('20 libros creados')
