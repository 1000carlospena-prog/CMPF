from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Carrito(models.Model):
    """Carrito de compras por usuario o sesión"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carrito'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        return f"Carrito Sesión {self.session_key}"

    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())

    @property
    def total_precio(self):
        return sum(item.subtotal for item in self.items.all())


class CarritoItem(models.Model):
    """Item dentro del carrito (producto o libro)"""
    carrito = models.ForeignKey(
        Carrito, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    
    # Generic Foreign Key para referenciar Producto o Libro
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contenido = GenericForeignKey('content_type', 'object_id')
    
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ['carrito', 'content_type', 'object_id']

    def __str__(self):
        return f"{self.cantidad} x {self.contenido}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario