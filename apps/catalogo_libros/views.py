from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify

from apps.productos.models import Producto, ProductoImagen
from apps.usuarios.decorators import grado_required


def listaLibros(request):
    libros_list = Producto.objects.filter(tipo='libro').order_by('nombre')
    query = request.GET.get('q')
    if query:
        libros_list = libros_list.filter(
            Q(nombre__icontains=query) |
            Q(metadata__autor__icontains=query)
        )
    genero = request.GET.get('genero')
    if genero:
        libros_list = libros_list.filter(metadata__genero=genero)
    paginator = Paginator(libros_list, 12)
    page = request.GET.get('page')
    try:
        libros = paginator.page(page)
    except PageNotAnInteger:
        libros = paginator.page(1)
    except EmptyPage:
        libros = paginator.page(paginator.num_pages)
    generos = Producto.objects.filter(tipo='libro').values_list('metadata__genero', flat=True).distinct().order_by('metadata__genero')
    generos = [g for g in generos if g]
    context = {
        'libros': libros,
        'query': query,
        'genero_seleccionado': genero,
        'generos': generos,
    }
    return render(request, 'catalogo/lista_libros.html', context)


def detalle_libro(request, id):
    libro = get_object_or_404(Producto, tipo='libro', id=id)
    return render(request, 'catalogo/detalle_libros.html', {'libro': libro})


@login_required
@grado_required('v3')
def crearLibro(request):
    if request.user.profile.grado == 'v3' and not request.user.profile.subscription_active:
        messages.error(request, 'Tu suscripción como proveedor no está activa. Renueva para publicar.')
        return redirect('upgrade')
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        autor = request.POST.get('autor', '').strip()
        genero = request.POST.get('genero', '').strip()
        precio = request.POST.get('precio', '').strip()
        sinopsis = request.POST.get('sinopsis', '').strip()
        if not all([nombre, autor, precio]):
            messages.error(request, 'Nombre, autor y precio son obligatorios.')
            return redirect('crearLibro')
        slug = slugify(nombre)
        if Producto.objects.filter(slug=slug).exists():
            slug = f'{slug}-{Producto.objects.filter(slug__startswith=slug).count()}'
        metadata = {'autor': autor, 'genero': genero, 'sinopsis': sinopsis}
        descripcion = sinopsis or f'Libro de {autor}.'
        if len(descripcion) > 500:
            descripcion = descripcion[:500]
        prod = Producto.objects.create(
            tipo='libro', nombre=nombre, slug=slug,
            descripcion=descripcion, precio=precio,
            existencia=1, disponible=True, metadata=metadata,
        )
        if 'imagen' in request.FILES:
            ProductoImagen.objects.create(producto=prod, imagen=request.FILES['imagen'], orden=0)
        messages.success(request, 'Libro creado correctamente')
        return redirect('detalle_libro', id=prod.id)
    return render(request, 'catalogo/crearLibro.html')
