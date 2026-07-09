from django.contrib import admin
from .models import Producto, ProductoImagen

class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    max_num = 4
    fields = ['imagen', 'orden']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'existencia', 'disponible']
    inlines = [ProductoImagenInline]