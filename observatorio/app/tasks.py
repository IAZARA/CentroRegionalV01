from celery import Celery
from app import create_app, db
from app.services.news_service import NewsService
from app.models import News
from datetime import datetime
import os

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

@celery.task
def update_news():
    """Tarea periódica para actualizar noticias"""
    with flask_app.app_context():
        try:
            news_service = NewsService()
            # Buscar noticias
            news_items = news_service.search_news()
            
            # Guardar cada noticia en la base de datos
            for item in news_items:
                # Verificar si la noticia ya existe por su URL
                existing_news = News.query.filter_by(url=item['link']).first()
                if not existing_news:
                    news = News(
                        title=item['title'],
                        content=item['snippet'],
                        url=item['link'],
                        source=item['source'],
                        country=item['country'],
                        keywords=item['keyword'],
                        published_date=item['published_date'],
                        created_at=datetime.now()
                    )
                    db.session.add(news)
            
            db.session.commit()
            return f"Se actualizaron las noticias exitosamente. {len(news_items)} noticias encontradas."
        except Exception as e:
            return f"Error actualizando noticias: {str(e)}"

# Configurar el horario de ejecución (8:00 AM hora de Argentina, UTC-3)
celery.conf.beat_schedule = {
    'actualizar-noticias-diariamente': {
        'task': 'app.tasks.update_news',
        'schedule': {'cron': {'hour': '8', 'minute': '0', 'timezone': 'America/Argentina/Buenos_Aires'}},
    },
}
