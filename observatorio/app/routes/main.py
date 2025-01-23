from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from datetime import datetime, timedelta
from app.models import News
from app.models.news_location import NewsLocation
from sqlalchemy import and_

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
    for country in ['.ar', '.cl', '.uy', '.py', '.bo', '.mx', '.co', '.pe', '.ec', '.ve']:
        countries[country] = News.query.filter(News.country == country).count()
    
    # Agregar conteo de noticias internacionales (sin país específico o con otro país)
    countries['other'] = News.query.filter(
        (News.country == None) | 
        (~News.country.in_(['.ar', '.cl', '.uy', '.py', '.bo', '.mx', '.co', '.pe', '.ec', '.ve']))
    ).count()
    
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

@bp.route('/api/news_locations')
@login_required
def get_news_locations():
    try:
        # Obtener parámetros de filtro
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        country = request.args.get('country')
        
        # Construir la consulta base
        query = NewsLocation.query.join(News)
        
        # Aplicar filtros si existen
        if start_date:
            query = query.filter(News.published_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(News.published_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        if country:
            query = query.filter(News.country == country)
            
        # Ejecutar la consulta
        locations = query.all()
        
        # Formatear resultados
        results = []
        for loc in locations:
            results.append({
                'id': loc.id,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'title': loc.news.title,
                'description': loc.news.content[:200] + '...' if loc.news.content else '',
                'date': loc.news.published_date.strftime('%Y-%m-%d') if loc.news.published_date else None,
                'url': loc.news.url,
                'location_name': loc.location_name,
                'country_code': loc.news.country
            })
        
        return jsonify({'locations': results})
    except Exception as e:
        current_app.logger.error(f"Error en get_news_locations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/geomap')
@login_required
def geomap():
    # Obtener el token de Mapbox desde las variables de entorno
    mapbox_token = current_app.config.get('MAPBOX_TOKEN')
    if not mapbox_token:
        flash('Error: No se encontró el token de Mapbox', 'error')
        return redirect(url_for('main.feed_new'))
    
    # Lista de países disponibles
    countries = [
        {'code': '.ar', 'name': 'Argentina'},
        {'code': '.cl', 'name': 'Chile'},
        {'code': '.uy', 'name': 'Uruguay'},
        {'code': '.py', 'name': 'Paraguay'},
        {'code': '.bo', 'name': 'Bolivia'}
    ]
    
    return render_template('main/geomap.html', 
                         mapbox_token=mapbox_token,
                         countries=countries)
