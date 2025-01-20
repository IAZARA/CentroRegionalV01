from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    return redirect(url_for('auth.login'))

@bp.route('/feed')
@login_required
def feed():
    country_filter = request.args.get('country', None)
    news_service = NewsService()
    
    # Obtener todas las noticias
    all_news = news_service.search_news()
    
    # Filtrar por país si se especifica
    if country_filter:
        filtered_news = [news for news in all_news if news.get('country') == country_filter]
    else:
        filtered_news = all_news
    
    # Calcular estadísticas
    current_time = datetime.now()
    stats = {
        'total': len(all_news),
        'news_last_24h': len([n for n in all_news if n.get('published_date') > (current_time - timedelta(days=1))]),
        'countries': {
            '.ar': {'name': 'Argentina', 'count': len([n for n in all_news if n.get('country') == '.ar'])},
            '.cl': {'name': 'Chile', 'count': len([n for n in all_news if n.get('country') == '.cl'])},
            '.uy': {'name': 'Uruguay', 'count': len([n for n in all_news if n.get('country') == '.uy'])},
            '.py': {'name': 'Paraguay', 'count': len([n for n in all_news if n.get('country') == '.py'])},
            '.bo': {'name': 'Bolivia', 'count': len([n for n in all_news if n.get('country') == '.bo'])}
        }
    }
    
    return render_template('main/feed.html', news=filtered_news, stats=stats)

@bp.route('/geomap')
@login_required
def geomap():
    news_service = NewsService()
    geocoding_service = GeocodingService()
    
    # Obtener noticias
    print("Buscando noticias...")
    news_items = news_service.search_news()
    print(f"Encontradas {len(news_items)} noticias")
    
    # Procesar cada noticia para obtener coordenadas
    markers = []
    for idx, news in enumerate(news_items):
        print(f"\nProcesando noticia {idx + 1}/{len(news_items)}")
        print(f"Título: {news.get('title')}")
        marker = geocoding_service.process_news_item(news)
        if marker:
            print(f"Coordenadas encontradas: {marker.get('coordinates')}")
            markers.append(marker)
        else:
            print("No se encontraron coordenadas para esta noticia")
    
    print(f"\nTotal de marcadores generados: {len(markers)}")
    
    # Obtener el token de Mapbox desde las variables de entorno
    mapbox_token = current_app.config.get('MAPBOX_TOKEN')
    if not mapbox_token:
        print("Error: No se encontró el token de Mapbox")
        flash('Error: No se encontró el token de Mapbox', 'error')
        return redirect(url_for('main.feed'))
    
    print(f"Token de Mapbox encontrado (primeros 10 caracteres): {mapbox_token[:10]}...")
    
    return render_template('main/geomap.html', 
                         mapbox_token=mapbox_token,
                         markers=markers)
