from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    existencia = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class ProductoImagen(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='productos/')
    orden = models.PositiveSmallIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'creado']
        verbose_name = 'Imagen del producto'
        verbose_name_plural = 'Imágenes del producto'

    def __str__(self):
        return f"Imagen {self.orden + 1} - {self.producto.nombre}"