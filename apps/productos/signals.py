from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.productos.models import Producto



# para despues de guardar un producto
@receiver(post_save, sender=Producto)
def producto_guardado(sender, instance, created, **kwargs):
    if created:
        print(f'Se a creado correctamente el producto: {instance.nombre}')
    else:
        print(f'Se a actualizado correctamente el producto: {instance.nombre}')

    if instance.existencia < 5:
        print(f'Atencion el producto "{instance.nombre}" tiene poca existencia: {instance.existencia} unidades restantes')

    if instance.existencia ==0:
        print(f'Alerta el producto: "{instance.nombre}" esta agotado')