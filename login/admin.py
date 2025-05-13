from django.contrib import admin
from .models import Estudiante, Reporte, Asistencia

admin.site.register(Estudiante)
admin.site.register(Reporte)
admin.site.register(Asistencia)