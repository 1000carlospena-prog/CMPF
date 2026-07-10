from django.contrib import admin
from .models import Categoria, Producto, ProductoImagen, Resena, ListaDeseos


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen


class ResenaInline(admin.TabularInline):
    model = Resena
    extra = 0


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'padre', 'activa', 'orden']
    prepopulated_fields = {'slug': ('nombre',)}
    list_filter = ['activa']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'precio_oferta', 'existencia', 'disponible', 'destacado']
    prepopulated_fields = {'slug': ('nombre',)}
    list_filter = ['disponible', 'destacado', 'categoria']
    search_fields = ['nombre', 'descripcion']
    inlines = [ProductoImagenInline, ResenaInline]


@admin.register(ProductoImagen)
class ProductoImagenAdmin(admin.ModelAdmin):
    list_display = ['producto', 'orden', 'creado']


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'puntuacion', 'creado']
    list_filter = ['puntuacion']
    search_fields = ['producto__nombre', 'usuario__username']


@admin.register(ListaDeseos)
class ListaDeseosAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'creado']
    search_fields = ['usuario__username', 'producto__nombre']
