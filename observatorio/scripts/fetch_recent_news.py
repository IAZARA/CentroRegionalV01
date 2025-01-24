from app import create_app, db
from app.services.news_service import NewsService
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
from app.services.anthropic_service import AnthropicService
from app.services.geocoding_service import GeocodingService
from app.models.news import News
from app.models.news_location import NewsLocation
from datetime import datetime, timedelta
import logging
import hashlib

def get_news_hash(title, url):
    """
    Genera un hash único para una noticia basado en su título y URL
    """
    hash_input = f"{title}{url}".encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

def fetch_recent_news():
    """
    Busca y geolocaliza noticias de los últimos 7 días sobre drogas sintéticas
    """
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Iniciando búsqueda de noticias...")
            
            # Inicializar servicios
            news_service = NewsService()
            geocoding_service = EnhancedGeocodingService()
            
            # Buscar noticias de los últimos 7 días
            keywords = [
                "drogas sintéticas argentina",
                "drogas de diseño argentina",
                "metanfetamina argentina",
                "éxtasis argentina",
                "mdma argentina",
                "fentanilo argentina",
                "ketamina argentina",
                "laboratorio clandestino drogas argentina",
                "narcotráfico drogas sintéticas argentina"
            ]
            
            # Conjunto para almacenar hashes de noticias ya procesadas
            processed_hashes = set()
            
            # Obtener noticias existentes
            existing_news = News.query.all()
            for news in existing_news:
                news_hash = get_news_hash(news.title, news.url)
                processed_hashes.add(news_hash)
            
            news_items = news_service.search_news(
                keywords=keywords,
                days=7,
                country='.ar'  # Filtrar solo noticias de Argentina
            )
            
            logger.info(f"Se encontraron {len(news_items)} noticias")
            
            # Procesar cada noticia
            for item in news_items:
                news_hash = get_news_hash(item['title'], item['link'])
                
                # Verificar si la noticia ya existe
                if news_hash in processed_hashes:
                    logger.info(f"La noticia ya existe: {item['title'][:50]}...")
                    continue
                
                logger.info(f"\nProcesando noticia: {item['title'][:50]}...")
                
                try:
                    # Crear nueva noticia
                    news = News(
                        title=item['title'],
                        content=item.get('snippet', ''),
                        url=item['link'],
                        source=item.get('source', ''),
                        country='ar',  # Forzar Argentina
                        published_date=item.get('published_date'),
                        keywords=', '.join(keywords)
                    )
                    db.session.add(news)
                    db.session.commit()
                    
                    # Agregar hash a procesados
                    processed_hashes.add(news_hash)
                    
                    # Extraer ubicaciones del título y contenido
                    text_to_analyze = f"{item['title']} {item.get('snippet', '')}"
                    logger.info(f"Analizando texto para ubicaciones: {text_to_analyze[:200]}...")
                    
                    locations = geocoding_service.extract_locations(text_to_analyze)
                    
                    location_count = 0
                    for loc in locations:
                        if loc.get('latitude') and loc.get('longitude'):
                            # Filtrar solo ubicaciones en Argentina
                            if loc.get('country_code', '').lower() == 'ar':
                                news_loc = NewsLocation(
                                    news_id=news.id,
                                    name=loc['name'],
                                    latitude=loc['latitude'],
                                    longitude=loc['longitude'],
                                    country_code='ar',
                                    is_primary=loc.get('is_primary', False)
                                )
                                db.session.add(news_loc)
                                location_count += 1
                    
                    if location_count > 0:
                        db.session.commit()
                        logger.info(f"Guardada con {location_count} ubicaciones en Argentina")
                    else:
                        logger.warning("No se encontraron ubicaciones válidas en Argentina")
                        
                except Exception as e:
                    logger.error(f"Error procesando noticia: {str(e)}")
                    db.session.rollback()
                    continue
            
            logger.info("\nProceso completado exitosamente!")
            
        except Exception as e:
            logger.error(f"Error durante el proceso: {str(e)}")
            db.session.rollback()

def test_geocoding():
    """
    Función para probar la geocodificación de una noticia específica
    """
    logger = logging.getLogger(__name__)
    logger.info("Iniciando prueba de geocodificación...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Inicializar servicios
            anthropic_service = AnthropicService()
            traditional_geocoding = GeocodingService()
            enhanced_geocoding = EnhancedGeocodingService()
            
            # Limpiar el caché para Mar del Plata
            traditional_geocoding.clear_cache("Mar del Plata, Argentina")
            
            # Texto de ejemplo
            title = "Desarticulan laboratorio de drogas sintéticas en Mar del Plata"
            text = """Desarticulan laboratorio de drogas sintéticas en Mar del Plata 
                    La Policía Federal Argentina desarticuló un laboratorio clandestino de drogas sintéticas 
                    en la ciudad de Mar del Plata, ubicado en el barrio La Perla. El operativo se realizó 
                    en conjunto con la Policía de la Provincia de Buenos Aires y la Fiscalía Federal de Constitución."""
            
            # Crear la noticia en la base de datos
            news = News(
                title=title,
                content=text,
                url="https://example.com/test",
                source="Test",
                country="ar",
                published_date=datetime.now(),
                keywords="drogas sintéticas, mar del plata"
            )
            db.session.add(news)
            db.session.commit()
            
            logger.info("Analizando texto para ubicaciones...")
            locations = anthropic_service.extract_locations(text)
            
            if locations:
                logger.info(f"Ubicaciones identificadas por IA: {locations}")
                location_count = 0
                
                for location in locations:
                    geocoded = enhanced_geocoding.geocode_location(location)
                    if geocoded:
                        # Crear ubicación en la base de datos
                        news_loc = NewsLocation(
                            news_id=news.id,
                            name=geocoded['name'],
                            latitude=geocoded['latitude'],
                            longitude=geocoded['longitude'],
                            country_code=geocoded['country_code'],
                            is_primary=geocoded['is_primary']
                        )
                        db.session.add(news_loc)
                        location_count += 1
                
                if location_count > 0:
                    db.session.commit()
                    logger.info(f"Noticia guardada con {location_count} ubicaciones")
                    
                    # Mostrar las ubicaciones guardadas
                    saved_locations = NewsLocation.query.filter_by(news_id=news.id).all()
                    logger.info("Ubicaciones guardadas en la base de datos:")
                    for loc in saved_locations:
                        logger.info(f"- {loc.name}: ({loc.latitude}, {loc.longitude})")
                else:
                    logger.warning("No se encontraron ubicaciones válidas")
            else:
                logger.warning("No se encontraron ubicaciones en el texto")
                
        except Exception as e:
            logger.error(f"Error durante la prueba: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    # fetch_recent_news()  # Comentado temporalmente
    logging.basicConfig(level=logging.INFO)
    test_geocoding()
