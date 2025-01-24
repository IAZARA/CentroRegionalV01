from app import create_app, db
from app.models.news import News
from app.models.news_location import NewsLocation
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
from datetime import datetime

def test_single_location():
    # Crear la aplicación con configuración de prueba
    app = create_app('config.TestingConfig')
    
    with app.app_context():
        # Limpiar la base de datos
        db.drop_all()
        db.create_all()
        
        # Crear noticia de prueba
        test_news = News(
            title="Desarticulan laboratorio de drogas sintéticas en Mar del Plata",
            content="Desarticulan laboratorio de drogas sintéticas en Mar del Plata La Policía Federal Argentina desarticuló un laboratorio clandestino de drogas sintéticas en la ...",
            url="http://test.com",
            source="Test",
            published_date=datetime.now()
        )
        
        db.session.add(test_news)
        db.session.commit()
        
        # Procesar la noticia
        geocoding_service = EnhancedGeocodingService()
        news_dict = {
            'id': test_news.id,
            'title': test_news.title,
            'content': test_news.content
        }
        
        location = geocoding_service.process_news_item(news_dict)
        
        if location:
            print(f"Ubicación encontrada: {location['name']}")
            print(f"Coordenadas: {location['latitude']}, {location['longitude']}")
            
            # Guardar la ubicación
            geocoding_service.traditional_service.save_location(location, news_dict)
            
            # Verificar que solo hay una ubicación
            locations = NewsLocation.query.filter_by(news_id=test_news.id).all()
            print(f"Número de ubicaciones: {len(locations)}")
            
            for loc in locations:
                print(f"- {loc.name} ({loc.latitude}, {loc.longitude})")
        else:
            print("No se encontró ninguna ubicación")

if __name__ == '__main__':
    test_single_location()
