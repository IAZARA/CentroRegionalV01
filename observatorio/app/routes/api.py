from flask import Blueprint, jsonify, request, current_app
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
        country_code = request.args.get('country_code')
        
        # Lista de códigos de país de América
        america_country_codes = [
            'ar', 'bo', 'br', 'cl', 'co', 'ec', 'gy', 'py', 'pe', 'sr', 'uy', 've',
            'mx', 'bz', 'cr', 'sv', 'gt', 'hn', 'ni', 'pa', 'cu', 'ht', 'do', 'us', 'ca'
        ]
        
        # Construir la consulta base
        query = NewsLocation.query\
            .join(News)\
            .filter(NewsLocation.country_code.in_(america_country_codes))\
            .order_by(desc(News.published_date))
        
        # Aplicar filtro de país si está presente
        if country_code:
            query = query.filter(NewsLocation.country_code == country_code.lower())
            
        # Aplicar filtros de fecha si están presentes
        if start_date:
            query = query.filter(News.published_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(News.published_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Limitar a las últimas 100 ubicaciones
        locations = query.limit(100).all()
        
        current_app.logger.info(f"Found {len(locations)} locations")
        
        result = [{
            'id': loc.id,
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'location_name': loc.name,
            'country_code': loc.country_code,
            'geocoding_confidence': loc.geocoding_confidence if hasattr(loc, 'geocoding_confidence') else None,
            'news': {
                'id': loc.news.id,
                'title': loc.news.title,
                'snippet': loc.news.summary,  
                'link': loc.news.url,  
                'source': loc.news.source,
                'published_date': loc.news.published_date.isoformat() if loc.news.published_date else None,
                'created_at': loc.news.created_at.isoformat()
            }
        } for loc in locations]
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_news_locations: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
