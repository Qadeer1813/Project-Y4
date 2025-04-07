from django.apps import AppConfig
from . import scheduler
import os

class CarenetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CareNet'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) == 'true':
            scheduler.start()