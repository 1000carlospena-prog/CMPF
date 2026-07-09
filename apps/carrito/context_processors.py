from .models import Carrito

def carrito(request):
    """Context processor para tener el carrito disponible en todos los templates"""
    carrito_obj = None
    
    if request.user.is_authenticated:
        carrito_obj, created = Carrito.objects.get_or_create(user=request.user)
    elif request.session.session_key:
        carrito_obj, created = Carrito.objects.get_or_create(session_key=request.session.session_key)
    else:
        # Crear sesión si no existe
        request.session.create()
        carrito_obj, created = Carrito.objects.get_or_create(session_key=request.session.session_key)
    
    return {
        'carrito': carrito_obj,
        'total_items_carrito': carrito_obj.total_items if carrito_obj else 0,
        'total_precio_carrito': carrito_obj.total_precio if carrito_obj else 0,
    }