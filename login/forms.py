from django import forms
from .models import Estudiante

class LoginForm(forms.Form):
    usuario = forms.CharField(label="Usuario")
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


# forms.py
from django import forms

class CargarExcelFormReporte(forms.Form):
    NIVEL_CHOICES = [
        ('', '---------'),         # Opción en blanco obligatoria
        ('30', 'Semillero (30 preguntas)'),
        ('90', 'Pre (90 preguntas)'),
    ]

    nivel = forms.ChoiceField(
        choices=NIVEL_CHOICES,
        required=True,
        label="Nivel del simulacro"
    )
    archivo_excel = forms.FileField(label="Seleccione un archivo Excel")
    
    



class CargarExcelForm(forms.Form):
    archivo_excel = forms.FileField(label="Seleccione un archivo Excel")

class EstudianteForm2(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'usuario', 'contraseña']
        widgets = {
            'contraseña': forms.PasswordInput(render_value=True),
        }

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['usuario', 'contraseña', 'nombre']
        widgets = {
            'contraseña': forms.PasswordInput(),  # Para que la contraseña se oculte al escribir
        }