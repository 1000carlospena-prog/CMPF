import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.productos.models import Producto

logger = logging.getLogger('cmpf.security')

@receiver(post_save, sender=Producto)
def producto_guardado(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Producto creado: {instance.nombre}')
    else:
        logger.info(f'Producto actualizado: {instance.nombre}')

    if instance.existencia < 5:
        logger.warning(f'Producto con stock bajo: {instance.nombre} - {instance.existencia} unidades')

    if instance.existencia == 0:
        logger.warning(f'Producto agotado: {instance.nombre}')
