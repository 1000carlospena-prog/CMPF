from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST

from apps.productos.models import Producto
from .models import Carrito, CarritoItem


def obtener_carrito(request):
    """Obtiene el carrito del usuario o sesión"""
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        carrito, created = Carrito.objects.get_or_create(session_key=request.session.session_key)
    return carrito


@require_POST
def agregar_al_carrito(request, content_type_id, object_id):
    """Agrega un item al carrito (funciona sin autenticación)"""
    carrito = obtener_carrito(request)
    
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    item = get_object_or_404(model_class, id=object_id)
    
    if hasattr(item, 'precio'):
        precio = item.precio
    else:
        messages.error(request, 'Este item no tiene precio')
        return redirect('home')
    
    carrito_item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        content_type=content_type,
        object_id=object_id,
        defaults={
            'precio_unitario': precio,
            'cantidad': 1
        }
    )
    
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    
    messages.success(request, f'✅ "{getattr(item, "nombre", "Item")}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@require_POST
def agregar_producto(request, producto_id):
    """Agrega un producto al carrito usando solo el ID del producto"""
    carrito = obtener_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    ct = ContentType.objects.get_for_model(Producto)
    
    carrito_item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        content_type=ct,
        object_id=producto_id,
        defaults={
            'precio_unitario': producto.precio_actual,
            'cantidad': 1
        }
    )
    
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    
    messages.success(request, f'✅ "{producto.nombre}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def ver_carrito(request):
    """Muestra el contenido del carrito"""
    carrito = obtener_carrito(request)
    context = {
        'carrito': carrito,
        'items': carrito.items.all(),
    }
    return render(request, 'carrito/ver.html', context)


@require_POST
def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un item"""
    carrito = obtener_carrito(request)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    
    cantidad = int(request.POST.get('cantidad', 0))
    if cantidad <= 0:
        item.delete()
        messages.success(request, '🗑️ Item eliminado del carrito.')
    else:
        item.cantidad = cantidad
        item.save()
        messages.success(request, '✅ Cantidad actualizada.')
    
    return redirect('carrito:ver')


@require_POST
def eliminar_item_carrito(request, item_id):
    """Elimina un item del carrito"""
    carrito = obtener_carrito(request)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    nombre = str(item.contenido)
    item.delete()
    messages.success(request, f'🗑️ "{nombre}" eliminado del carrito.')
    return redirect('carrito:ver')


def vaciar_carrito(request):
    """Vacia todo el carrito"""
    carrito = obtener_carrito(request)
    carrito.items.all().delete()
    messages.success(request, '🗑️ Carrito vaciado correctamente.')
    return redirect('carrito:ver')