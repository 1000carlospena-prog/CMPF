from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from apps.productos.models import Categoria, Producto, ProductoImagen
from apps.catalogo_libros.models import Autor, Editora, Generos, Libros
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import io
import os
import hashlib


class Command(BaseCommand):
    help = 'Seeds 20 products and 20 books'

    def handle(self, *args, **options):
        self._seed_categorias()
        self._seed_productos()
        self._seed_libros()
        self.stdout.write(self.style.SUCCESS('Seed data created successfully'))

    def _generate_image(self, label, filename, w=400, h=400):
        colors = [
            (52, 152, 219), (231, 76, 60), (46, 204, 113), (155, 89, 182),
            (241, 196, 15), (230, 126, 34), (26, 188, 156), (149, 165, 166),
            (44, 62, 80), (243, 156, 18), (192, 57, 43), (41, 128, 185),
            (39, 174, 96), (142, 68, 173), (22, 160, 133), (127, 140, 141),
            (211, 84, 0), (84, 153, 199), (125, 60, 152), (46, 139, 87),
        ]
        idx = int(hashlib.md5(label.encode()).hexdigest(), 16) % len(colors)
        bg = colors[idx]

        img = Image.new('RGB', (w, h), bg)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype('arial.ttf', 28)
        except Exception:
            font = ImageFont.load_default()

        lines = []
        words = label.split()
        line = ''
        for word in words:
            test = f'{line} {word}'.strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > w - 40:
                lines.append(line)
                line = word
            else:
                line = test
        lines.append(line)

        total_h = len(lines) * 36
        y_start = (h - total_h) // 2
        for i, l in enumerate(lines):
            bbox = draw.textbbox((0, 0), l, font=font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            draw.text((x, y_start + i * 36), l, fill='white', font=font)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        img.save(filepath)
        return filename

    def _seed_categorias(self):
        categorias = [
            'Electrónica', 'Ropa y Accesorios', 'Hogar', 'Deportes',
            'Juguetes', 'Salud y Belleza', 'Automotriz', 'Mascotas',
        ]
        for nombre in categorias:
            Categoria.objects.get_or_create(
                nombre=nombre,
                slug=slugify(nombre),
            )
        self.stdout.write(f'{len(categorias)} categorias creadas')

    def _seed_productos(self):
        productos_data = [
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
        for nombre, cat_nombre, precio, oferta, existencia, destacado in productos_data:
            cat = Categoria.objects.get(nombre=cat_nombre)
            slug = slugify(nombre)
            prod, created = Producto.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    categoria=cat,
                    nombre=nombre,
                    descripcion=f'{nombre} de alta calidad al mejor precio.',
                    precio=precio,
                    precio_oferta=oferta,
                    existencia=existencia,
                    destacado=destacado,
                ),
            )
            if created:
                filename = f'producto_{slug}.jpg'
                self._generate_image(nombre, filename)
                ProductoImagen.objects.create(producto=prod, imagen=filename, orden=0)
        self.stdout.write(f'{len(productos_data)} productos creados')

    def _seed_libros(self):
        autor1, _ = Autor.objects.get_or_create(nombre='Gabriel', apellido='García Márquez')
        autor2, _ = Autor.objects.get_or_create(nombre='Isabel', apellido='Allende')
        autor3, _ = Autor.objects.get_or_create(nombre='Jorge Luis', apellido='Borges')
        autor4, _ = Autor.objects.get_or_create(nombre='Mario', apellido='Vargas Llosa')
        autor5, _ = Autor.objects.get_or_create(nombre='Julio', apellido='Cortázar')
        autor6, _ = Autor.objects.get_or_create(nombre='Carlos', apellido='Fuentes')
        autor7, _ = Autor.objects.get_or_create(nombre='Pablo', apellido='Neruda')
        autor8, _ = Autor.objects.get_or_create(nombre='Gabriela', apellido='Mistral')
        autor9, _ = Autor.objects.get_or_create(nombre='Juan', apellido='Rulfo')
        autor10, _ = Autor.objects.get_or_create(nombre='Octavio', apellido='Paz')

        editora1, _ = Editora.objects.get_or_create(nombreEditora='Alfaguara', ciudad='Madrid')
        editora2, _ = Editora.objects.get_or_create(nombreEditora='Planeta', ciudad='Barcelona')
        editora3, _ = Editora.objects.get_or_create(nombreEditora='Anagrama', ciudad='Barcelona')
        editora4, _ = Editora.objects.get_or_create(nombreEditora='Sudamericana', ciudad='Buenos Aires')
        editora5, _ = Editora.objects.get_or_create(nombreEditora='Fondo Cultura', ciudad='Ciudad de México')

        generos_list = ['Novela', 'Poesía', 'Cuento', 'Ensayo', 'Ficción']
        generos = {}
        for g in generos_list:
            obj, _ = Generos.objects.get_or_create(tipoGenero=g)
            generos[g] = obj

        libros_data = [
            ('Cien años de soledad', autor1, generos['Novela'], editora4, 19.99, date(1967, 6, 5), 'La historia de la familia Buendía en Macondo.'),
            ('El amor en tiempos del cólera', autor1, generos['Novela'], editora4, 17.99, date(1985, 9, 5), 'Una historia de amor que espera medio siglo.'),
            ('La casa de los espíritus', autor2, generos['Novela'], editora1, 16.99, date(1982, 1, 1), 'Saga familiar con elementos mágicos.'),
            ('Paula', autor2, generos['Ensayo'], editora1, 14.99, date(1994, 1, 1), 'Memorias dedicadas a su hija.'),
            ('Ficciones', autor3, generos['Cuento'], editora3, 15.99, date(1944, 1, 1), 'Colección de cuentos fantásticos.'),
            ('El Aleph', autor3, generos['Cuento'], editora3, 14.99, date(1949, 1, 1), 'Cuentos sobre infinito y laberintos.'),
            ('La ciudad y los perros', autor4, generos['Novela'], editora1, 16.99, date(1963, 1, 1), 'Vida en un colegio militar de Lima.'),
            ('Conversación en La Catedral', autor4, generos['Novela'], editora1, 18.99, date(1969, 1, 1), 'Retrato del Perú bajo el régimen de Odría.'),
            ('Rayuela', autor5, generos['Novela'], editora3, 17.99, date(1963, 1, 1), 'Novela experimental y saltarina.'),
            ('Bestiario', autor5, generos['Cuento'], editora3, 13.99, date(1951, 1, 1), 'Primera colección de cuentos de Cortázar.'),
            ('La muerte de Artemio Cruz', autor6, generos['Novela'], editora5, 15.99, date(1962, 1, 1), 'Vida de un revolucionario mexicano en su lecho de muerte.'),
            ('Aura', autor6, generos['Novela'], editora5, 12.99, date(1962, 1, 1), 'Novela corta de misterio y fantasía.'),
            ('Veinte poemas de amor', autor7, generos['Poesía'], editora4, 11.99, date(1924, 1, 1), 'Poemario de amor juvenil.'),
            ('Confieso que he vivido', autor7, generos['Ensayo'], editora4, 14.99, date(1974, 1, 1), 'Autobiografía del poeta.'),
            ('Desolación', autor8, generos['Poesía'], editora4, 12.99, date(1922, 1, 1), 'Primer gran poemario de Mistral.'),
            ('Tala', autor8, generos['Poesía'], editora4, 11.99, date(1938, 1, 1), 'Poemario que refleja la madurez poética.'),
            ('Pedro Páramo', autor9, generos['Novela'], editora5, 13.99, date(1955, 1, 1), 'Novela sobre un pueblo fantasma.'),
            ('El llano en llamas', autor9, generos['Cuento'], editora5, 12.99, date(1953, 1, 1), 'Cuentos de la Revolución Mexicana.'),
            ('El laberinto de la soledad', autor10, generos['Ensayo'], editora5, 14.99, date(1950, 1, 1), 'Ensayo sobre la identidad mexicana.'),
            ('Piedra de sol', autor10, generos['Poesía'], editora5, 10.99, date(1957, 1, 1), 'Poema extenso y emblemático.'),
        ]
        for nombre, autor, genero, editora, precio, fecha, sinopsis in libros_data:
            slug = slugify(nombre)
            libro, created = Libros.objects.get_or_create(
                nombreLibro=nombre,
                defaults=dict(
                    autor=autor,
                    genero=genero,
                    editora=editora,
                    precio=precio,
                    fechaPublicacion=fecha,
                    sinopsis=sinopsis,
                ),
            )
            if created:
                filename = f'libro_{slug}.jpg'
                self._generate_image(nombre, filename, w=200, h=300)
                libro.imagen = filename
                libro.save()
        self.stdout.write(f'{len(libros_data)} libros creados')
