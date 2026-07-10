from django.contrib import admin
from .models import Orden, OrdenItem


class OrdenItemInline(admin.TabularInline):
    model = OrdenItem


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'total', 'creado']
    list_filter = ['estado', 'creado']
    search_fields = ['usuario__username', 'nombre_completo']
    inlines = [OrdenItemInline]
    readonly_fields = ['total']
