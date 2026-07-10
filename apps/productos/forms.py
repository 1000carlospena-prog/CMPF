from django import forms
from .models import Producto, Resena


class ProductoConImagenesForm(forms.ModelForm):
    imagen1 = forms.ImageField(required=False, label='Imagen 1')
    imagen2 = forms.ImageField(required=False, label='Imagen 2')
    imagen3 = forms.ImageField(required=False, label='Imagen 3')
    imagen4 = forms.ImageField(required=False, label='Imagen 4')

    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'precio_oferta', 'existencia', 'disponible', 'destacado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'star-input'}),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu opinión...'}),
        }
