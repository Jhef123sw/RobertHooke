from django.contrib.auth.backends import BaseBackend
from .models import Estudiante

class EstudianteBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            estudiante = Estudiante.objects.get(usuario=username)
            if estudiante.contraseña == password:
                return estudiante
            else:
                return None
        except Estudiante.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Estudiante.objects.get(pk=user_id)
        except Estudiante.DoesNotExist:
            return None