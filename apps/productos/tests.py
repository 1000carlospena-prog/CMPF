from django.test import TestCase
from django.contrib.auth.models import User
from apps.productos.models import Categoria, Producto, ProductoImagen, Resena, ListaDeseos


class CategoriaModelTest(TestCase):
    def test_crear_categoria(self):
        cat = Categoria.objects.create(nombre='Electrónica', slug='electronica')
        self.assertEqual(str(cat), 'Electrónica')
        self.assertTrue(cat.activa)


class ProductoModelTest(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nombre='Test', slug='test')

    def test_crear_producto(self):
        p = Producto.objects.create(
            categoria=self.cat, nombre='Producto Test',
            descripcion='Desc', precio=10.00, existencia=5
        )
        self.assertEqual(p.precio_actual, 10.00)
        self.assertFalse(p.en_oferta)

    def test_producto_en_oferta(self):
        p = Producto.objects.create(
            categoria=self.cat, nombre='Oferta',
            descripcion='Desc', precio=20.00, precio_oferta=15.00, existencia=10
        )
        self.assertEqual(p.precio_actual, 15.00)
        self.assertTrue(p.en_oferta)

    def test_stock_bajo_signal(self):
        import logging
        logger = logging.getLogger('cmpf.security')
        with self.assertLogs('cmpf.security', level='WARNING') as log:
            Producto.objects.create(
                categoria=self.cat, nombre='Bajo Stock',
                descripcion='Desc', precio=5.00, existencia=2
            )
            self.assertTrue(any('stock bajo' in msg.lower() for msg in log.output))


class ProductoImagenModelTest(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nombre='Test', slug='test')
        self.prod = Producto.objects.create(
            categoria=cat, nombre='Test', descripcion='Desc', precio=10.00, existencia=5
        )

    def test_display_url_externa(self):
        img = ProductoImagen.objects.create(
            producto=self.prod, url_externa='https://example.com/img.jpg'
        )
        self.assertEqual(img.display_url, 'https://example.com/img.jpg')
