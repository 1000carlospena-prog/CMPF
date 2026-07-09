from django.contrib import admin
from .models import Carrito, CarritoItem

class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0
    readonly_fields = ['precio_unitario', 'subtotal']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'total_precio', 'creado']
    list_filter = ['creado']
    search_fields = ['user__username', 'session_key']
    inlines = [CarritoItemInline]
    readonly_fields = ['total_items', 'total_precio']

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    def total_precio(self, obj):
        return f"${obj.total_precio:.2f}"
    total_precio.short_description = 'Total Precio'