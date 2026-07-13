from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q

from apps.productos.models import Producto
from apps.carrito.models import CarritoItem
from django.contrib.auth.models import User


@login_required
def dashboard(request):
    total_productos = Producto.objects.count()
    productos_disponibles = Producto.objects.filter(disponible=True).count()
    productos_no_disponibles = Producto.objects.filter(disponible=False).count()
    productos_stock_bajo = Producto.objects.filter(existencia__lt=5, existencia__gt=0).count()
    productos_agotados = Producto.objects.filter(existencia=0).count()
    
    productos_mas_stock = Producto.objects.order_by('-existencia')[:5]
    productos_menos_stock = Producto.objects.filter(existencia__gt=0).order_by('existencia')[:5]
    
    total_existencias = Producto.objects.aggregate(total=Sum('existencia'))['total'] or 0
    precio_promedio = Producto.objects.aggregate(promedio=Sum('precio') / Count('id'))['promedio'] or 0
    
    libros_qs = Producto.objects.filter(tipo='libro')
    total_libros = libros_qs.count()
    total_autores = libros_qs.values('metadata__autor').distinct().count()
    total_generos = libros_qs.values('metadata__genero').distinct().count()
    
    libros_por_genero = libros_qs.values('metadata__genero').annotate(
        total=Count('id')
    ).filter(total__gt=0).order_by('-total')
    
    libros_por_autor = libros_qs.values('metadata__autor').annotate(
        total=Count('id')
    ).filter(total__gt=0).order_by('-total')[:10]
    
    ultimos_libros = libros_qs.order_by('-creado')[:5]
    
    total_items_carrito = CarritoItem.objects.count()
    items_mas_vendidos = CarritoItem.objects.values(
        'content_type__app_label', 
        'content_type__model'
    ).annotate(total=Count('id')).order_by('-total')[:5]
    
    context = {
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'productos_no_disponibles': productos_no_disponibles,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'productos_mas_stock': productos_mas_stock,
        'productos_menos_stock': productos_menos_stock,
        'total_existencias': total_existencias,
        'precio_promedio': precio_promedio,
        
        'total_libros': total_libros,
        'total_autores': total_autores,
        'total_generos': total_generos,
        'total_editoras': 0,
        'libros_por_genero': libros_por_genero,
        'libros_por_autor': libros_por_autor[:5],
        'ultimos_libros': ultimos_libros,
        
        'total_items_carrito': total_items_carrito,
        'items_mas_vendidos': items_mas_vendidos,
    }
    
    return render(request, 'dashboard/index.html', context)