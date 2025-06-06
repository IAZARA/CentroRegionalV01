from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, session
from flask_login import login_required, current_user, logout_user
from app.services.news_service import NewsService
from app.services.geocoding_service import GeocodingService
from datetime import datetime, timedelta
from app.models import News
from app.models.news_location import NewsLocation
from sqlalchemy import and_
import os
from app.models.user import UserRoles
from app.main import bp

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.home'))

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
    # Funcionalidad migrada a Looker Pro - redirigir o mostrar mensaje
    current_app.logger.info("Acceso a geomap - funcionalidad migrada a Looker Pro")
    
    # Lista de países disponibles (mantenida para compatibilidad)
    countries = [
        {'code': '.ar', 'name': 'Argentina'},
        {'code': '.cl', 'name': 'Chile'},
        {'code': '.uy', 'name': 'Uruguay'},
        {'code': '.py', 'name': 'Paraguay'},
        {'code': '.bo', 'name': 'Bolivia'}
    ]
    
    return render_template('main/geomap.html',
                         countries=countries)

@bp.route('/legislation')
@login_required
def legislation():
    return render_template('main/legislation.html')

@bp.route('/analisis-tecnico')
@login_required
def analisis_tecnico():
    return render_template('main/analisis_tecnico.html')

@bp.route('/agenda')
@login_required
def agenda():
    return render_template('main/agenda.html')

@bp.route('/set_language/<language_code>')
def set_language(language_code):
    # Agregar logs detallados para depurar
    current_app.logger.info(f"Cambiando idioma a: {language_code}")
    current_app.logger.info(f"Idiomas configurados: {current_app.config.get('LANGUAGES')}")
    current_app.logger.info(f"Sesión actual: {dict(session)}")
    
    # Asegurarse de que el código de idioma sea uno de los idiomas soportados
    supported_languages = current_app.config.get('LANGUAGES', ['es', 'en', 'pt'])
    if language_code not in supported_languages:
        flash(f'Idioma seleccionado ({language_code}) no válido. Opciones: {supported_languages}', 'danger')
        return redirect(request.referrer or url_for('main.home'))

    # Guardar en sesión
    session['language'] = language_code
    session.modified = True  # Forzar la actualización de la sesión
    current_app.logger.info(f"Sesión actualizada: {dict(session)}")
    
    # Preparar JSON para respuesta AJAX o redirección normal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'language': language_code})
    
    # Respuesta normal con redirección
    flash(f'Idioma cambiado a: {language_code}', 'success')
    redirect_url = request.referrer or url_for('main.home')
    current_app.logger.info(f"Redireccionando a: {redirect_url}")
    return redirect(redirect_url)

@bp.route('/browser_translate/<language_code>')
def browser_translate(language_code):
    """Ruta para activar la traducción del navegador con JavaScript"""
    if language_code not in ['es', 'en', 'pt']:
        return jsonify({'success': False, 'message': 'Idioma no soportado'})
        
    # No necesitamos guardar nada en la sesión, solo devolver el código de idioma
    # para que el JavaScript lo maneje
    return jsonify({
        'success': True,
        'language': language_code,
        'language_name': {
            'es': 'Español',
            'en': 'English',
            'pt': 'Português'
        }.get(language_code, 'Unknown')
    })

@bp.route('/force_logout')
def force_logout():
    logout_user()
    return 'Logged out'
