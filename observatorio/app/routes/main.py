from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from datetime import datetime, timedelta
from app.models import News

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.route('/noticias')
@login_required
def feed_new():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obtener las noticias paginadas
    pagination = News.query.order_by(News.published_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    # Estadísticas generales
    total_news = News.query.count()
    news_last_24h = News.query.filter(
        News.published_date >= datetime.now() - timedelta(days=1)
    ).count()
    
    # Estadísticas por país
    countries = {}
    for country in ['.ar', '.cl', '.uy', '.py', '.bo']:
        countries[country] = News.query.filter(News.country == country).count()
    
    stats = {
        'total': total_news,
        'news_last_24h': news_last_24h,
        'by_country': countries
    }
    
    return render_template(
        'main/feed_new.html',
        news=pagination.items,
        pagination=pagination,
        stats=stats
    )

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
        return redirect(url_for('main.feed_new'))
    
    print(f"Token de Mapbox encontrado (primeros 10 caracteres): {mapbox_token[:10]}...")
    
    return render_template('main/geomap.html', 
                         mapbox_token=mapbox_token,
                         markers=markers)
