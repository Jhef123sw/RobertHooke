from django.contrib import admin
from .models import Estudiante, Reporte, Asistencia, curso

admin.site.register(Estudiante)
admin.site.register(Reporte)
admin.site.register(Asistencia)
admin.site.register(curso)