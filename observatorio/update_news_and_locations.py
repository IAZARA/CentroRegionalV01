#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models.news import News
from app.models.news_location import NewsLocation
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

def update_news_and_locations():
    """
    Actualiza las noticias y sus ubicaciones geográficas de las últimas 24 horas
    """
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando actualización de noticias y ubicaciones...")
        
        # 1. Actualizar noticias
        print("\n📰 Actualizando noticias de las últimas 24 horas...")
        news_service = NewsService()
        
        # Obtener noticias de las últimas 24 horas
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        try:
            # Obtener las URLs existentes en la base de datos
            existing_urls = {url[0] for url in db.session.query(News.url).all()}
            
            # Buscar nuevas noticias
            new_news = news_service.search_news(days=1)  # Buscar noticias del último día
            
            # Filtrar noticias que ya existen
            new_news_filtered = [news for news in new_news if news['link'] not in existing_urls]
            
            if not new_news_filtered:
                print("ℹ️ No hay nuevas noticias para agregar")
                return
            
            # Contador de noticias agregadas
            added_count = 0
            
            # Guardar solo las noticias nuevas
            for news_data in new_news_filtered:
                try:
                    news = News(
                        title=news_data['title'],
                        content=news_data.get('snippet', ''),
                        url=news_data['link'],
                        published_date=news_data.get('published_date', datetime.now())
                    )
                    db.session.add(news)
                    db.session.commit()
                    added_count += 1
                except IntegrityError:
                    # Si hay un error de duplicado, hacer rollback y continuar
                    db.session.rollback()
                    print(f"⚠️ La noticia ya existe: {news_data['link']}")
                    continue
                except Exception as e:
                    db.session.rollback()
                    print(f"⚠️ Error agregando noticia: {str(e)}")
                    continue
            
            if added_count > 0:
                print(f"✅ Se agregaron {added_count} nuevas noticias")
            else:
                print("ℹ️ No se agregaron nuevas noticias")
                return
            
        except Exception as e:
            print(f"❌ Error actualizando noticias: {str(e)}")
            return
        
        # 2. Procesar ubicaciones solo para las nuevas noticias
        print("\n🌍 Procesando ubicaciones geográficas...")
        try:
            # Obtener solo las noticias nuevas sin ubicaciones
            news_without_locations = News.query.outerjoin(
                NewsLocation, News.id == NewsLocation.news_id
            ).filter(
                NewsLocation.id.is_(None),
                News.published_date >= start_date
            ).all()
            
            if not news_without_locations:
                print("✅ Todas las noticias nuevas ya tienen ubicaciones procesadas")
                return
            
            print(f"📍 Procesando ubicaciones para {len(news_without_locations)} noticias...")
            geocoding_service = GeocodingService()
            
            for news in news_without_locations:
                try:
                    # Procesar ubicaciones para cada noticia
                    locations = geocoding_service.extract_locations(news.content)
                    for location in locations:
                        geocoded = geocoding_service.geocode_location(location)
                        if geocoded:
                            news_location = NewsLocation(
                                news_id=news.id,
                                location_name=location,
                                latitude=geocoded['latitude'],
                                longitude=geocoded['longitude'],
                                country_code=geocoded.get('country_code', 'ar')
                            )
                            db.session.add(news_location)
                    
                    print(f"✅ Procesada noticia ID: {news.id}")
                except Exception as e:
                    print(f"⚠️ Error procesando ubicaciones para noticia {news.id}: {str(e)}")
                    continue
            
            db.session.commit()
            print("\n✅ Proceso completado exitosamente!")
            
        except Exception as e:
            print(f"❌ Error en el proceso de geocodificación: {str(e)}")
            return

if __name__ == "__main__":
    update_news_and_locations()
