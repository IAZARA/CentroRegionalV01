from celery import Celery
from app import create_app
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from app.models.news import News
from app.models.news_location import NewsLocation
from datetime import datetime
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

@celery.task
def update_news():
    """Tarea periódica para actualizar noticias"""
    with flask_app.app_context():
        try:
            news_service = NewsService()
            geocoding_service = GeocodingService()
            # Buscar noticias
            news_items = news_service.search_news()
            
            news_count = 0
            locations_count = 0
            
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
                    db.session.flush()  # Para obtener el ID de la noticia
                    news_count += 1
                    
                    # Extraer y geocodificar ubicaciones
                    text = f"{item['title']} {item['snippet']}"
                    locations = geocoding_service.extract_locations(text)
                    for location in locations:
                        coords = geocoding_service.geocode_location(location)
                        if coords:
                            lat, lon = coords
                            geocoding_service.save_location(news.id, location, lat, lon)
                            locations_count += 1
            
            db.session.commit()
            return f"Se actualizaron las noticias exitosamente. {news_count} noticias y {locations_count} ubicaciones encontradas."
        except Exception as e:
            db.session.rollback()
            return f"Error actualizando noticias: {str(e)}"

@celery.task
def process_existing_news():
    """
    Procesa todas las noticias existentes para extraer y geocodificar ubicaciones
    """
    from app import db
    
    geocoding_service = GeocodingService()
    news_items = News.query.all()
    
    for news in news_items:
        try:
            # Procesar la noticia para extraer y geocodificar ubicaciones
            if news.content:
                locations = geocoding_service.extract_locations(news.content)
                logger.info(f"Ubicaciones encontradas en noticia {news.id}: {locations}")
                
                for location in locations:
                    coords = geocoding_service.geocode_location(location)
                    if coords:
                        lat, lng = coords
                        news_location = NewsLocation(
                            news_id=news.id,
                            location_name=location,
                            latitude=lat,
                            longitude=lng,
                            country_code=geocoding_service._get_country_code(location)
                        )
                        db.session.add(news_location)
                        logger.info(f"Ubicación agregada: {location} ({lat}, {lng})")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error procesando noticia {news.id}: {str(e)}")
            db.session.rollback()
            continue

# Configurar el horario de ejecución (8:00 AM hora de Argentina, UTC-3)
celery.conf.beat_schedule = {
    'actualizar-noticias-diariamente': {
        'task': 'app.tasks.update_news',
        'schedule': {'cron': {'hour': '8', 'minute': '0', 'timezone': 'America/Argentina/Buenos_Aires'}},
    },
}
