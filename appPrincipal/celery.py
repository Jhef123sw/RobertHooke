import os
from celery import Celery

# Apunta al archivo settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appPrincipal.settings')

# Nombre del app de Celery (puede ser el mismo que el del proyecto base)
app = Celery('RobertHooke')

# Carga configuración desde settings.py con el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas dentro de todas las apps
app.autodiscover_tasks()
