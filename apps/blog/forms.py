from django import forms
from .models import Comentario


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'placeholder': 'Escribe tu comentario...',
                'rows': 4,
            }),
        }
        labels = {
            'texto': '',
        }
