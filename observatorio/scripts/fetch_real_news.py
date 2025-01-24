from app import create_app, db
from app.models.news import News
from app.services.news_service import NewsService
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
from datetime import datetime

def fetch_and_process_news():
    app = create_app()
    with app.app_context():
        # Resetear la base de datos
        db.drop_all()
        db.create_all()
        print("Base de datos reiniciada")
        
        # Crear servicios
        news_service = NewsService()
        geocoding_service = EnhancedGeocodingService()
        
        # Obtener noticias reales
        search_terms = [
            'drogas sintéticas',
            'drogas de diseño',
            'metanfetamina',
            'éxtasis',
            'MDMA',
            'fentanilo',
            'ketamina',
            'LSD',
            'narcotráfico sintético',
            'laboratorio drogas',
            'nuevas drogas',
            'drogas químicas',
            'tusi',
            'cocaina rosa',
            'anfetaminas'
        ]
        
        all_news = []
        for term in search_terms:
            print(f"\nBuscando noticias con término: {term}")
            news_items = news_service.search_news(
                search_term=term,
                days=3,      # Últimos 3 días
            )
            all_news.extend(news_items)
        
        # Filtrar noticias relevantes y eliminar duplicados
        processed_urls = set()
        relevant_news = []
        
        for item in all_news:
            url = item.get('link')
            if url in processed_urls:
                continue
                
            if news_service.is_news_relevant(item['title'], item.get('snippet', '')):
                relevant_news.append(item)
                processed_urls.add(url)
                
            if len(relevant_news) >= 20:
                break
        
        print(f"Procesando {len(relevant_news)} noticias...")
        
        # Procesar cada noticia
        successful_news = []
        
        for item in relevant_news:
            try:
                # Crear la noticia
                news = News(
                    title=item['title'],
                    content=item.get('snippet', ''),
                    url=item['link'],
                    source=item.get('source', 'Desconocido'),
                    published_date=datetime.now()  # O usar item['date'] si está disponible
                )
                db.session.add(news)
                db.session.commit()
                
                print(f"\nProcesando noticia: {news.title}")
                
                # Procesar ubicaciones
                location = geocoding_service.process_news_item({
                    'id': news.id,
                    'title': news.title,
                    'content': news.content
                })
                
                if location:
                    print(f"Ubicación encontrada: {location['name']}")
                    geocoding_service.traditional_service.save_location(location, {'id': news.id})
                    successful_news.append(news)
                else:
                    print("No se encontró ubicación")
                    # Si no se encuentra ubicación, eliminar la noticia
                    db.session.delete(news)
                    db.session.commit()
                    
            except Exception as e:
                print(f"Error procesando noticia: {str(e)}")
                db.session.rollback()
                continue
        
        print("\nProceso completado")
        
        # Mostrar resumen
        print(f"\nResumen:")
        print(f"Total de noticias cargadas: {len(successful_news)}")
        
        # Mostrar las noticias y sus ubicaciones
        for news in successful_news:
            print(f"\nNoticia: {news.title}")
            for location in news.locations:
                print(f"- Ubicación: {location.name} ({location.latitude}, {location.longitude})")

if __name__ == '__main__':
    fetch_and_process_news()
