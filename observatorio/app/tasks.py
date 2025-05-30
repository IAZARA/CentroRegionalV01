from celery import Celery
from app import create_app
import os
import logging

logger = logging.getLogger(__name__)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery = make_celery(flask_app)

# Las tareas de procesamiento de noticias y geocodificación han sido eliminadas
# tras la migración a iFrames de Looker Pro.
# Este archivo mantiene la configuración básica de Celery para futuras tareas.

# Configuración de horarios de ejecución (actualmente vacía)
celery.conf.beat_schedule = {}
