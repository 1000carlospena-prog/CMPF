from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


TIPO_PRODUCTO_CHOICES = [
    ('general', 'General'),
    ('gastronomico', 'Gastronómico'),
    ('digital', 'Digital'),
    ('libro', 'Libro'),
    ('domestico', 'Doméstico'),
    ('servicio', 'Servicio'),
    ('inmueble', 'Inmueble'),
    ('vehiculo', 'Vehículo'),
    ('evento', 'Evento'),
    ('empleo', 'Empleo'),
    ('arte', 'Arte / Música'),
]


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hijas')
    icono = models.CharField(max_length=50, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    tipo = models.CharField(max_length=20, choices=TIPO_PRODUCTO_CHOICES, default='general')
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    descripcion = models.TextField(max_length=500)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    existencia = models.IntegerField(default=0)
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadatos extra (autor, género, etc.)')
    creado = models.DateTimeField(auto_now_add=True, null=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.nombre}'

    @property
    def precio_actual(self):
        return self.precio_oferta if self.precio_oferta else self.precio

    @property
    def en_oferta(self):
        return self.precio_oferta is not None

    @property
    def descuento_porcentaje(self):
        if self.precio_oferta:
            return int((1 - float(self.precio_oferta) / float(self.precio)) * 100)
        return 0

    @property
    def rating_promedio(self):
        resenas = self.resenas.all()
        if resenas:
            return sum(r.puntuacion for r in resenas) / resenas.count()
        return 0

    @property
    def total_resenas(self):
        return self.resenas.count()


class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    url_externa = models.URLField(blank=True, verbose_name='URL externa (fallback para producción)')
    orden = models.PositiveSmallIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'creado']
        verbose_name = 'Imagen del producto'
        verbose_name_plural = 'Imágenes del producto'

    def __str__(self):
        return f'Imagen {self.orden + 1} - {self.producto.nombre}'

    @property
    def display_url(self):
        try:
            if self.imagen and self.imagen.storage.exists(self.imagen.name):
                return self.imagen.url
        except Exception:
            pass
        return self.url_externa or ''


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos_stock')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_stock')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    saldo_anterior = models.IntegerField()
    saldo_posterior = models.IntegerField()
    nota = models.CharField(max_length=255, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'{self.tipo} {self.cantidad} - {self.producto.nombre}'


class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas')
    puntuacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(max_length=500)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['producto', 'usuario']
        ordering = ['-creado']

    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre} ({self.puntuacion}/5)'


class ListaDeseos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lista_deseos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='en_deseos')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'producto']
        verbose_name_plural = 'Listas de deseos'

    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre}'
