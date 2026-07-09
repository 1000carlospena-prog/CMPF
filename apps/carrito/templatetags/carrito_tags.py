from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def content_type_id(obj):
    """Obtiene el ID del ContentType de un objeto"""
    return ContentType.objects.get_for_model(obj).id

@register.filter
def subtotal(item):
    """Calcula el subtotal de un item"""
    return item.cantidad * item.precio_unitario

@register.simple_tag
def total_items(carrito):
    """Total de items en el carrito"""
    return carrito.total_items if carrito else 0

@register.simple_tag
def total_precio(carrito):
    """Total del carrito"""
    return carrito.total_precio if carrito else 0