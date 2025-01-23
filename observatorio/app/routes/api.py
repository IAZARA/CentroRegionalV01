from flask import Blueprint, jsonify, request
from app.models.news_location import NewsLocation
from app.models.news import News
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('api', __name__)

@bp.route('/news/locations')
def get_news_locations():
    """
    Obtener todas las ubicaciones de noticias con sus detalles
    """
    try:
        # Obtener parámetros de filtro
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Construir la consulta base
        query = NewsLocation.query\
            .join(News)\
            .filter(NewsLocation.country_code == 'ar')\
            .order_by(desc(News.published_date))
        
        # Aplicar filtros de fecha si están presentes
        if start_date:
            query = query.filter(News.published_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(News.published_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Limitar a las últimas 100 ubicaciones
        locations = query.limit(100).all()

        return jsonify([{
            'id': loc.id,
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'location_name': loc.location_name,
            'country_code': loc.country_code,
            'geocoding_confidence': loc.geocoding_confidence,
            'news': {
                'id': loc.news.id,
                'title': loc.news.title,
                'snippet': loc.news.snippet,
                'link': loc.news.link,
                'source': loc.news.source,
                'published_date': loc.news.published_date.isoformat() if loc.news.published_date else None,
                'created_at': loc.news.created_at.isoformat()
            }
        } for loc in locations])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
