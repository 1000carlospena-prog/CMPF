from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Producto, ProductoImagen, Categoria, Resena, ListaDeseos
from .forms import ProductoConImagenesForm, ResenaForm
from .serializers import ProductoSerializer
from rest_framework import viewsets
from apps.usuarios.mixins import GradoRequiredMixin, PublicadorRequiredMixin
from apps.usuarios.decorators import grado_required
from apps.usuarios.models import Profile


class ProductoVista(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Producto.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | Q(descripcion__icontains=query)
            )
        categoria_slug = self.request.GET.get('categoria')
        if categoria_slug:
            cat = get_object_or_404(Categoria, slug=categoria_slug)
            hijas = cat.hijas.values_list('id', flat=True)
            queryset = queryset.filter(categoria_id__in=[cat.id] + list(hijas))
        disponible = self.request.GET.get('disponible')
        if disponible == 'si':
            queryset = queryset.filter(disponible=True)
        elif disponible == 'no':
            queryset = queryset.filter(disponible=False)
        stock = self.request.GET.get('stock')
        if stock == 'bajo':
            queryset = queryset.filter(existencia__lt=5, existencia__gt=0)
        elif stock == 'agotado':
            queryset = queryset.filter(existencia=0)
        orden = self.request.GET.get('orden')
        if orden == 'precio':
            queryset = queryset.order_by('precio')
        elif orden == '-precio':
            queryset = queryset.order_by('-precio')
        elif orden == 'nombre':
            queryset = queryset.order_by('nombre')
        else:
            queryset = queryset.order_by('-creado')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['filtro_disponible'] = self.request.GET.get('disponible', '')
        context['filtro_stock'] = self.request.GET.get('stock', '')
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        context['orden_actual'] = self.request.GET.get('orden', '')
        context['categorias'] = Categoria.objects.filter(activa=True, padre__isnull=True)
        return context


class ProductoDetalle(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = self.object
        context['resenas'] = producto.resenas.select_related('usuario').all()
        context['productos_relacionados'] = Producto.objects.filter(
            categoria=producto.categoria
        ).exclude(id=producto.id)[:4]
        if self.request.user.is_authenticated:
            context['en_deseos'] = ListaDeseos.objects.filter(
                usuario=self.request.user, producto=producto
            ).exists()
            usuario_resena = producto.resenas.filter(usuario=self.request.user).first()
            if usuario_resena:
                context['mi_resena'] = usuario_resena
            context['review_form'] = ResenaForm()
        return context


@login_required
def agregar_resena(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.resenas.filter(usuario=request.user).exists():
        messages.error(request, 'Ya has reseñado este producto.')
        return redirect('productos:detalle_producto', pk=producto_id)
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.producto = producto
            resena.usuario = request.user
            resena.save()
            messages.success(request, 'Reseña publicada.')
    return redirect('productos:detalle_producto', pk=producto_id)


@login_required
def toggle_deseo(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    item, created = ListaDeseos.objects.get_or_create(
        usuario=request.user, producto=producto
    )
    if not created:
        item.delete()
        messages.info(request, f'"{producto.nombre}" eliminado de tu lista de deseos.')
    else:
        messages.success(request, f'"{producto.nombre}" añadido a tu lista de deseos.')
    return redirect('productos:detalle_producto', pk=producto_id)


@login_required
def lista_deseos(request):
    items = ListaDeseos.objects.filter(usuario=request.user).select_related('producto')
    return render(request, 'productos/lista_deseos.html', {'items': items})


class ProductoCrear(PublicadorRequiredMixin, CreateView):
    grado_minimo = 'v3'
    model = Producto
    form_class = ProductoConImagenesForm
    template_name = 'productos/crear.html'
    success_url = reverse_lazy('productos:lista_productos')

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.vendedor = self.request.user
        producto.save()
        imagenes = [
            form.cleaned_data.get(f'imagen{i}')
            for i in range(1, 5)
        ]
        guardadas = 0
        for i, img in enumerate(imagenes):
            if img:
                ProductoImagen.objects.create(producto=producto, imagen=img, orden=i)
                guardadas += 1
        messages.success(self.request, f'Producto "{producto.nombre}" creado con {guardadas} imágenes.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el producto. Revisa los campos.')
        return super().form_invalid(form)


class ProductoActualizar(PublicadorRequiredMixin, UpdateView):
    grado_minimo = 'v3'
    model = Producto
    form_class = ProductoConImagenesForm
    template_name = 'productos/actualizar.html'
    success_url = reverse_lazy('productos:lista_productos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imagenes_existentes'] = self.object.imagenes.all()
        return context

    def form_valid(self, form):
        producto = form.save()
        for i in range(1, 5):
            img = form.cleaned_data.get(f'imagen{i}')
            if img:
                ProductoImagen.objects.create(producto=producto, imagen=img, orden=i - 1)
        messages.success(self.request, f'Producto "{producto.nombre}" actualizado.')
        return super().form_valid(form)


class ProductosEliminar(PublicadorRequiredMixin, DeleteView):
    grado_minimo = 'v3'
    model = Producto
    template_name = 'productos/eliminar.html'
    success_url = reverse_lazy('productos:lista_productos')

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        messages.success(self.request, f'Producto "{producto.nombre}" eliminado.')
        return super().delete(request, *args, **kwargs)


@grado_required('v3')
def eliminar_imagen(request, imagen_id):
    if request.user.profile.grado == 'v3' and not request.user.profile.subscription_active:
        messages.error(request, 'Tu suscripción como proveedor no está activa.')
        return redirect('upgrade')
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    pid = imagen.producto.id
    imagen.delete()
    messages.success(request, 'Imagen eliminada.')
    return redirect('productos:actualizar_producto', pk=pid)


@login_required
def mi_inventario(request):
    productos = Producto.objects.filter(vendedor=request.user).order_by('-creado')
    return render(request, 'productos/inventario.html', {'productos': productos})


@login_required
@require_POST
def ajustar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, vendedor=request.user)
    try:
        cantidad = int(request.POST.get('cantidad', 0))
        tipo = request.POST.get('tipo', 'entrada')
    except (ValueError, TypeError):
        messages.error(request, 'Cantidad inválida.')
        return redirect('productos:mi_inventario')

    if cantidad <= 0:
        messages.error(request, 'La cantidad debe ser mayor a cero.')
        return redirect('productos:mi_inventario')

    saldo_anterior = producto.existencia
    if tipo == 'entrada':
        producto.existencia += cantidad
        nota = request.POST.get('nota', '')
    elif tipo == 'salida':
        if cantidad > producto.existencia:
            messages.error(request, 'Stock insuficiente para esa salida.')
            return redirect('productos:mi_inventario')
        producto.existencia -= cantidad
        nota = request.POST.get('nota', '')
    else:
        messages.error(request, 'Tipo de movimiento inválido.')
        return redirect('productos:mi_inventario')

    producto.save()

    from .models import MovimientoStock
    MovimientoStock.objects.create(
        producto=producto,
        usuario=request.user,
        tipo=tipo,
        cantidad=cantidad,
        saldo_anterior=saldo_anterior,
        saldo_posterior=producto.existencia,
        nota=nota,
    )

    action = 'entrada' if tipo == 'entrada' else 'salida'
    messages.success(request, f'Stock ajustado: +{cantidad if tipo == "entrada" else f"-{cantidad}"} ({action}). Nuevo stock: {producto.existencia}')
    return redirect('productos:mi_inventario')


class ProductoViewset(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
