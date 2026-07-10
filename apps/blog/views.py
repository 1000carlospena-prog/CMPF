from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Post, Comentario
from .forms import ComentarioForm


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comentarios'] = self.object.comentarios.filter(padre__isnull=True, activo=True)
        ctx['form'] = ComentarioForm()
        return ctx


@require_POST
@login_required
def agregar_comentario(request, slug):
    post = get_object_or_404(Post, slug=slug, publicado=True)
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.post = post
        comentario.autor = request.user
        padre_id = request.POST.get('padre')
        if padre_id:
            try:
                comentario.padre = Comentario.objects.get(id=padre_id, post=post)
            except Comentario.DoesNotExist:
                pass
        comentario.save()
        messages.success(request, 'Comentario publicado.')
    else:
        messages.error(request, 'Error al publicar comentario.')
    return redirect('blog:detalle', slug=slug)
