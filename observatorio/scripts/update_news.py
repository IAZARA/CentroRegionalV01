#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime, timedelta
from app import create_app, db
from app.models.news import News
from app.models.news_location import NewsLocation
from app.services.news_service import NewsService
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

def update_news(reprocess_all=False, days=1, hours=None):
    """
    Actualiza las noticias y sus ubicaciones geográficas
    
    Args:
        reprocess_all (bool): Si es True, reprocesa todas las noticias existentes
        days (int): Número de días hacia atrás para buscar noticias
        hours (int): Número de horas hacia atrás para buscar noticias (tiene precedencia sobre days)
    """
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando actualización de noticias y ubicaciones...")
        
        # 1. Actualizar noticias
        time_window = f"{hours} horas" if hours else f"{days} días"
        print(f"\n📰 Buscando noticias de las últimas {time_window}...")
        news_service = NewsService()
        
        try:
            # Obtener las URLs existentes
            existing_urls = {url[0] for url in db.session.query(News.url).all()}
            
            # Términos de búsqueda para drogas sintéticas
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
                print(f"\n🔍 Buscando noticias con término: {term}")
                if hours:
                    news_items = news_service.search_news(search_term=term, hours=hours)
                else:
                    news_items = news_service.search_news(search_term=term, days=days)
                all_news.extend(news_items)
            
            # Filtrar noticias que ya existen
            new_news_filtered = [news for news in all_news if news['link'] not in existing_urls]
            
            if not new_news_filtered:
                print("ℹ️ No hay nuevas noticias para agregar")
            else:
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
            
        except Exception as e:
            print(f"❌ Error actualizando noticias: {str(e)}")
            return
        
        # 2. Procesar ubicaciones
        print("\n🌍 Procesando ubicaciones geográficas...")
        try:
            if reprocess_all:
                # Si reprocess_all es True, eliminar todas las ubicaciones existentes
                NewsLocation.query.delete()
                db.session.commit()
                # Obtener todas las noticias
                news_to_process = News.query.all()
            else:
                # Obtener solo las noticias sin ubicaciones
                news_to_process = News.query.outerjoin(
                    NewsLocation, News.id == NewsLocation.news_id
                ).filter(
                    NewsLocation.id.is_(None)
                ).all()
            
            if not news_to_process:
                print("✅ No hay noticias para procesar")
                return
            
            print(f"📍 Procesando ubicaciones para {len(news_to_process)} noticias...")
            geocoding_service = EnhancedGeocodingService()
            
            for news in news_to_process:
                try:
                    # Procesar ubicaciones para cada noticia
                    locations = geocoding_service.process_news_item({
                        'text': news.content,
                        'title': news.title
                    })
                    
                    for location in locations:
                        try:
                            news_location = NewsLocation(
                                news_id=news.id,
                                name=location['name'],
                                latitude=location['latitude'],
                                longitude=location['longitude'],
                                country_code=location['country_code'],
                                is_primary=location['is_primary']
                            )
                            db.session.add(news_location)
                        except Exception as e:
                            print(f"⚠️ Error guardando ubicación: {str(e)}")
                            continue
                    
                    db.session.commit()
                    print(f"✅ Procesada noticia ID: {news.id}")
                except Exception as e:
                    db.session.rollback()
                    print(f"⚠️ Error procesando noticia ID {news.id}: {str(e)}")
                    continue
            
            print("\n✅ Proceso completado exitosamente!")
            
        except Exception as e:
            print(f"❌ Error procesando ubicaciones: {str(e)}")
            return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Actualiza noticias y ubicaciones')
    parser.add_argument('--reprocess-all', action='store_true', 
                       help='Reprocesa todas las noticias existentes')
    parser.add_argument('--days', type=int, default=1,
                       help='Número de días hacia atrás para buscar noticias')
    parser.add_argument('--hours', type=int,
                       help='Número de horas hacia atrás para buscar noticias (tiene precedencia sobre days)')
    args = parser.parse_args()
    
    update_news(reprocess_all=args.reprocess_all, days=args.days, hours=args.hours)
