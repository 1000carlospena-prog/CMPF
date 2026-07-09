from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import Producto, ProductoImagen
from .forms import ProductoConImagenesForm
from .serializers import ProductoSerializer
from rest_framework import generics, viewsets
from apps.usuarios.mixins import GradoRequiredMixin, PublicadorRequiredMixin
from apps.usuarios.decorators import grado_required


class ProductoVista(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 12  # ✅ Productos por página

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # ✅ BÚSQUEDA por nombre o descripción
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query)
            )
        
        # ✅ FILTRO por disponibilidad
        disponible = self.request.GET.get('disponible')
        if disponible == 'si':
            queryset = queryset.filter(disponible=True)
        elif disponible == 'no':
            queryset = queryset.filter(disponible=False)
        
        # ✅ FILTRO por existencia (stock bajo)
        stock = self.request.GET.get('stock')
        if stock == 'bajo':
            queryset = queryset.filter(existencia__lt=5, existencia__gt=0)
        elif stock == 'agotado':
            queryset = queryset.filter(existencia=0)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ Mantener filtros en la paginación
        context['query'] = self.request.GET.get('q', '')
        context['filtro_disponible'] = self.request.GET.get('disponible', '')
        context['filtro_stock'] = self.request.GET.get('stock', '')
        return context


class ProductoDetalle(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'
    context_object_name = 'producto'


class ProductoCrear(PublicadorRequiredMixin, CreateView):
    grado_minimo = 'v3'
    model = Producto
    form_class = ProductoConImagenesForm
    template_name = 'productos/crear.html'
    success_url = reverse_lazy('productos:lista_productos')

    def form_valid(self, form):
        producto = form.save()

        imagenes = [
            form.cleaned_data.get('imagen1'),
            form.cleaned_data.get('imagen2'),
            form.cleaned_data.get('imagen3'),
            form.cleaned_data.get('imagen4'),
        ]

        imagenes_guardadas = 0
        for i, imagen in enumerate(imagenes):
            if imagen:
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=imagen,
                    orden=i
                )
                imagenes_guardadas += 1

        messages.success(
            self.request,
            f'✅ Producto "{producto.nombre}" creado con {imagenes_guardadas} imágenes.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        print("❌ Errores del formulario:", form.errors)
        messages.error(self.request, '❌ Error al crear el producto. Revisa los campos.')
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

        imagenes = [
            form.cleaned_data.get('imagen1'),
            form.cleaned_data.get('imagen2'),
            form.cleaned_data.get('imagen3'),
            form.cleaned_data.get('imagen4'),
        ]

        imagenes_guardadas = 0
        for i, imagen in enumerate(imagenes):
            if imagen:
                ProductoImagen.objects.create(
                    producto=producto,
                    imagen=imagen,
                    orden=i
                )
                imagenes_guardadas += 1

        if imagenes_guardadas > 0:
            messages.success(
                self.request,
                f'✅ Producto "{producto.nombre}" actualizado con {imagenes_guardadas} imágenes nuevas.'
            )
        else:
            messages.success(self.request, f'✅ Producto "{producto.nombre}" actualizado correctamente.')

        return super().form_valid(form)

    def form_invalid(self, form):
        print("❌ Errores del formulario:", form.errors)
        messages.error(self.request, '❌ Error al actualizar el producto. Revisa los campos.')
        return super().form_invalid(form)


class ProductosEliminar(PublicadorRequiredMixin, DeleteView):
    grado_minimo = 'v3'
    model = Producto
    template_name = 'productos/eliminar.html'
    success_url = reverse_lazy('productos:lista_productos')

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        messages.success(self.request, f'✅ Producto "{producto.nombre}" eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


from apps.usuarios.models import Profile

@grado_required('v3')
def eliminar_imagen(request, imagen_id):
    if request.user.profile.grado == 'v3' and not request.user.profile.subscription_active:
        messages.error(request, 'Tu suscripción como proveedor no está activa.')
        return redirect('upgrade')
    imagen = get_object_or_404(ProductoImagen, id=imagen_id)
    producto_id = imagen.producto.id
    imagen.delete()
    messages.success(request, '🗑️ Imagen eliminada correctamente.')
    return redirect('productos:actualizar_producto', pk=producto_id)


# API Views
class ProductoListaApi(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class ProductoViewset(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer