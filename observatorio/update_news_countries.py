from app import create_app, db
from app.models import News
from app.services.geocoding_service import GeocodingService
from flask import current_app

def update_news_countries():
    app = create_app()
    with app.app_context():
        geocoding_service = GeocodingService()
        
        # Obtener todas las noticias
        news = News.query.all()
        print(f"Actualizando {len(news)} noticias...")
        
        for i, news_item in enumerate(news, 1):
            try:
                # Procesar la noticia con el servicio de geocodificación actualizado
                processed = geocoding_service.process_news_item({
                    'id': news_item.id,
                    'title': news_item.title,
                    'description': news_item.content,
                    'link': news_item.url
                })
                
                if processed and processed.get('locations'):
                    # Tomar el primer país encontrado
                    country_code = processed['locations'][0]['country_code']
                    if country_code:
                        news_item.country = f".{country_code}"
                        print(f"[{i}/{len(news)}] Actualizada noticia {news_item.id} - País: {country_code}")
                    else:
                        print(f"[{i}/{len(news)}] No se encontró país para la noticia {news_item.id}")
                else:
                    print(f"[{i}/{len(news)}] No se pudo procesar la noticia {news_item.id}")
                
                # Guardar cada 10 noticias
                if i % 10 == 0:
                    db.session.commit()
                    
            except Exception as e:
                print(f"Error procesando noticia {news_item.id}: {str(e)}")
                continue
        
        # Guardar los cambios restantes
        db.session.commit()
        print("¡Actualización completada!")

if __name__ == '__main__':
    update_news_countries()
