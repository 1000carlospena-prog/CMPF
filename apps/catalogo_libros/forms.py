from django import forms
from .models import Libros
from datetime import datetime, date



class LibrosForm(forms.ModelForm):
    class Meta:
        model = Libros
        fields = '__all__'
        widgets = {
            'fechaPublicacion': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'fechaPublicacion': 'Ingresa la fecha )'
        }

    def clean_fechaPublicacion(self):
        fecha = self.cleaned_data.get('fechaPublicacion')
        if not fecha:
            return None

        # Si ya es un objeto date, lo devolvemos tal cual
        if isinstance(fecha, (date, datetime)):
            if isinstance(fecha, datetime):
                return fecha.date()
            return fecha

        # Intentamos parsear la fecha manualmente
        formatos = [
            '%Y-%m-%d',  # 2024-02-13
            '%d/%m/%Y',  # 13/02/2024
            '%Y-%d-%m',
            '%d-%m-%Y',  # 13-02-2024
            '%m/%d/%Y',  # 02/13/2024
            '%m-%d-%Y',  # 02-13-2024
        ]
        for fmt in formatos:
            try:
                return datetime.strptime(str(fecha), fmt).date()
            except ValueError:
                continue

        raise forms.ValidationError(
            "Formato de fecha no reconocido. Usa algo como 2024-02-13 o 13/02/2024."
        )
	