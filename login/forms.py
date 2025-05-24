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
        (30, 'Semillero (35 preguntas)'),
        (90, 'Pre (90 preguntas)'),
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
        
        #widgets = {
        #    'contraseña': forms.PasswordInput(),  # Para que la contraseña se oculte al escribir
        #}

class ActualizarDatosForm(forms.ModelForm):
    GRADO_CHOICES = [
        (1, '1° de Secundaria'),
        (2, '2° de Secundaria'),
        (3, '3° de Secundaria'),
        (4, '4° de Secundaria'),
        (5, '5° de Secundaria'),
        (6, 'Egresado'),
    ]
    nombre = forms.CharField(required=True, label="¿Tu nombre está bien escrito?")
    colegio = forms.CharField(required=True, label="¿En qué colegio estudias o estudiaste?")
    grado = forms.ChoiceField(
        choices=GRADO_CHOICES,
        required=True,
        label="¿Cuál es tu grado actual de estudios?"
    )
    ciudad = forms.CharField(required=True, label="¿De qué ciudad nos visitas?")
    numCelular = forms.CharField(required=True, label="Número de celular (De preferencia que tenga Whatsapp)")
    instagram = forms.CharField(required=True, label="¿Cómo te encontramos en instagram?")
    facebook = forms.CharField(required=True, label="¿Cómo te encontramos en Facebook?")
    carrera = forms.CharField(required=True, label="¿A qué carrera deseas postular?")
    class Meta:
        model = Estudiante
        fields = ['nombre','colegio', 'grado', 'ciudad', 'numCelular', 'instagram', 'facebook', 'carrera']