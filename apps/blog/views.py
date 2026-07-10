from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Post


class BlogLista(ListView):
    model = Post
    template_name = 'blog/lista.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(publicado=True)


class BlogDetalle(DetailView):
    model = Post
    template_name = 'blog/detalle.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(publicado=True)
