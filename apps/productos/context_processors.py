from .models import Categoria


def categorias(request):
    return {
        'categorias': Categoria.objects.filter(activa=True, padre__isnull=True).prefetch_related('hijas'),
    }
