from django import forms
from .models import Producto, ProductoImagen

class ProductoConImagenesForm(forms.ModelForm):
    imagen1 = forms.ImageField(
        required=False,
        label='Imagen 1',
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    imagen2 = forms.ImageField(
        required=False,
        label='Imagen 2',
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    imagen3 = forms.ImageField(
        required=False,
        label='Imagen 3',
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    imagen4 = forms.ImageField(
        required=False,
        label='Imagen 4',
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'existencia', 'disponible']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'existencia': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['imagen1', 'imagen2', 'imagen3', 'imagen4']:
            if field_name in self.fields:
                self.fields[field_name].required = False