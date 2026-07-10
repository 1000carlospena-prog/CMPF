from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q

from apps.productos.models import Producto
from apps.catalogo_libros.models import Libros, Autor, Generos, Editora
from apps.carrito.models import CarritoItem


@login_required
def dashboard(request):
    total_productos = Producto.objects.count()
    productos_disponibles = Producto.objects.filter(disponible=True).count()
    productos_no_disponibles = Producto.objects.filter(disponible=False).count()
    productos_stock_bajo = Producto.objects.filter(existencia__lt=5, existencia__gt=0).count()
    productos_agotados = Producto.objects.filter(existencia=0).count()
    
    # Productos con más existencia
    productos_mas_stock = Producto.objects.order_by('-existencia')[:5]
    
    # Productos con menos existencia
    productos_menos_stock = Producto.objects.filter(existencia__gt=0).order_by('existencia')[:5]
    
    # Total de existencias
    total_existencias = Producto.objects.aggregate(total=Sum('existencia'))['total'] or 0
    precio_promedio = Producto.objects.aggregate(promedio=Sum('precio') / Count('id'))['promedio'] or 0
    
    total_libros = Libros.objects.count()
    total_autores = Autor.objects.count()
    total_generos = Generos.objects.count()
    total_editoras = Editora.objects.count()
    
    # Libros por género
    libros_por_genero = Generos.objects.annotate(
        total=Count('libros')
    ).filter(total__gt=0).order_by('-total')
    
    # Libros por autor
    libros_por_autor = Autor.objects.annotate(
        total=Count('libros')
    ).filter(total__gt=0).order_by('-total')[:10]
    
    # Últimos libros agregados
    ultimos_libros = Libros.objects.order_by('-id')[:5]
    
    total_items_carrito = CarritoItem.objects.count()
    items_mas_vendidos = CarritoItem.objects.values(
        'content_type__app_label', 
        'content_type__model'
    ).annotate(total=Count('id')).order_by('-total')[:5]
    
    context = {
        # Productos
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'productos_no_disponibles': productos_no_disponibles,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'productos_mas_stock': productos_mas_stock,
        'productos_menos_stock': productos_menos_stock,
        'total_existencias': total_existencias,
        'precio_promedio': precio_promedio,
        
        # Libros
        'total_libros': total_libros,
        'total_autores': total_autores,
        'total_generos': total_generos,
        'total_editoras': total_editoras,
        'libros_por_genero': libros_por_genero,
        'libros_por_autor': libros_por_autor[:5],
        'ultimos_libros': ultimos_libros,
        
        # Carrito
        'total_items_carrito': total_items_carrito,
        'items_mas_vendidos': items_mas_vendidos,
    }
    
    return render(request, 'dashboard/index.html', context)