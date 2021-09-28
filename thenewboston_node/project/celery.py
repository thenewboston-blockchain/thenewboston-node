import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thenewboston_node.project.settings')
app = Celery('thenewboston_node')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
