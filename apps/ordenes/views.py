from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Orden, OrdenItem
from apps.carrito.models import Carrito, CarritoItem


@login_required
def checkout(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = CarritoItem.objects.filter(carrito=carrito).select_related('producto')
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito:ver')

    total = sum(item.subtotal for item in items)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        provincia = request.POST.get('provincia', '').strip()
        codigo = request.POST.get('codigo_postal', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        notas = request.POST.get('notas', '').strip()

        if not all([nombre, direccion, ciudad, provincia, telefono]):
            messages.error(request, 'Completa todos los campos obligatorios.')
            return render(request, 'ordenes/checkout.html', {
                'items': items, 'total': total, 'carrito': carrito
            })

        with transaction.atomic():
            orden = Orden.objects.create(
                usuario=request.user,
                total=total,
                nombre_completo=nombre,
                direccion=direccion,
                ciudad=ciudad,
                provincia=provincia,
                codigo_postal=codigo,
                telefono=telefono,
                notas=notas,
            )
            for item in items:
                producto = item.producto
                if producto.existencia < item.cantidad:
                    messages.error(request, f'Stock insuficiente para "{producto.nombre}".')
                    return redirect('carrito:ver')
                producto.existencia -= item.cantidad
                producto.save(update_fields=['existencia'])
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    producto_nombre=producto.nombre,
                    precio=producto.precio_actual,
                    cantidad=item.cantidad,
                )
            items.delete()

        messages.success(request, f'Orden #{orden.id} creada con éxito. Recibirás un correo de confirmación.')
        return redirect('ordenes:detalle', orden_id=orden.id)

    return render(request, 'ordenes/checkout.html', {
        'items': items, 'total': total, 'carrito': carrito
    })


@login_required
def historial(request):
    ordenes = Orden.objects.filter(usuario=request.user).prefetch_related('items')
    return render(request, 'ordenes/historial.html', {'ordenes': ordenes})


@login_required
def detalle(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'ordenes/detalle.html', {'orden': orden})
