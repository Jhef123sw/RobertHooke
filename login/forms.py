from django import forms
from .models import Estudiante, Asistencia, VariableControl

class LoginForm(forms.Form):
    usuario = forms.CharField(label="Usuario")
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

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

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['usuario', 'contraseña', 'nombre']

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
    numCelular = forms.CharField(required=True, label="Número de celular (Que tenga Whatsapp)")
    instagram = forms.CharField(required=True, label="¿Cómo te encontramos en instagram?")
    facebook = forms.CharField(required=True, label="¿Cómo te encontramos en Facebook?")
    carrera = forms.CharField(required=True, label="¿A qué carrera deseas postular?")
    class Meta:
        model = Estudiante
        fields = ['nombre','colegio', 'grado', 'ciudad', 'numCelular', 'instagram', 'facebook', 'carrera']

class AsistenciaForm(forms.ModelForm):
    MODALIDAD_CHOICES = [
        'PRESENCIAL', 'VIRTUAL'
    ]
    class Meta:
        model = Asistencia
        fields = ['KK_usuario', 'Fecha', 'Observacion', 'Modalidad']


class AsistenciaForm2(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['KK_usuario', 'Fecha', 'Hora', 'Observacion', 'Modalidad']
        widgets = {
            'KK_usuario': forms.Select(attrs={
                'class': 'form-select', 'id': 'kk-usuario-select'
            }),
            'Fecha': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control'
            }),
            'Hora': forms.TimeInput(format='%H:%M', attrs={
                'type': 'time', 'class': 'form-control'
            }),
            'Observacion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Escriba alguna observación...'
            }),
            'Modalidad': forms.Select(choices=[('PRESENCIAL', 'PRESENCIAL'), ('VIRTUAL', 'VIRTUAL')],
                                      attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo incluir estudiantes con tipo_estudiante activo
        self.fields['KK_usuario'].queryset = Estudiante.objects.filter(tipo_estudiante__iexact='estudiante')

class VariableControlForm(forms.ModelForm):
    class Meta:
        model = VariableControl
        fields = '__all__'
        widgets = {
            'EntradaManana': forms.TimeInput(attrs={'type': 'time'}),
            'SalidaManana': forms.TimeInput(attrs={'type': 'time'}),
            'EntradaTarde': forms.TimeInput(attrs={'type': 'time'}),
            'SalidaTarde': forms.TimeInput(attrs={'type': 'time'}),
            'EntradaAmanecida': forms.TimeInput(attrs={'type': 'time'}),
            'SalidaAmanecida': forms.TimeInput(attrs={'type': 'time'}),
        }
        