from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.catalogo_libros.models import Libros, Generos
from apps.catalogo_libros.forms import LibrosForm
from apps.usuarios.decorators import grado_required

def listaLibros(request):
    libros_list = Libros.objects.all().order_by('nombreLibro')
    query = request.GET.get('q')
    if query:
        libros_list = libros_list.filter(
            Q(nombreLibro__icontains=query) |
            Q(autor__nombre__icontains=query) |
            Q(autor__apellido__icontains=query)
        )
    genero_id = request.GET.get('genero')
    if genero_id:
        libros_list = libros_list.filter(genero_id=genero_id)
    editora_id = request.GET.get('editora')
    if editora_id:
        libros_list = libros_list.filter(editora_id=editora_id)
    paginator = Paginator(libros_list, 12)
    page = request.GET.get('page')
    try:
        libros = paginator.page(page)
    except PageNotAnInteger:
        libros = paginator.page(1)
    except EmptyPage:
        libros = paginator.page(paginator.num_pages)
    generos = Generos.objects.all().order_by('tipoGenero')
    context = {
        'libros': libros,
        'query': query,
        'genero_seleccionado': genero_id,
        'generos': generos,
    }
    return render(request, 'catalogo/lista_libros.html', context)

def detalle_libro(request, id):
    libro = get_object_or_404(Libros, id=id)
    return render(request, 'catalogo/detalle_libros.html', {'libro': libro})

@login_required
@grado_required('v3')
def crearLibro(request):
    if request.user.profile.grado == 'v3' and not request.user.profile.subscription_active:
        messages.error(request, 'Tu suscripción como proveedor no está activa. Renueva para publicar.')
        return redirect('upgrade')
    if request.method == 'POST':
        action = request.POST.get('action')
            if action == 'logout':
                auth_logout(request)
                return redirect('login')
        elif action == 'guardarLibro' or action == 'guardar':
            form = LibrosForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Libro creado correctamente')
                return redirect('crearLibro')
            else:
                messages.error(request, 'Error al crear libro')
    else:
        form = LibrosForm()

    return render(request, 'catalogo/crearLibro.html', {'form': form})

