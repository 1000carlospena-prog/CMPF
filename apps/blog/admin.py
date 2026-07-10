from django.contrib import admin
from .models import Post, Comentario


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    fields = ['autor', 'texto', 'activo']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'publicado', 'destacado', 'creado']
    list_filter = ['publicado', 'destacado']
    search_fields = ['titulo', 'contenido']
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [ComentarioInline]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'post', 'creado', 'activo']
    list_filter = ['activo', 'creado']
    search_fields = ['texto', 'autor__username']
