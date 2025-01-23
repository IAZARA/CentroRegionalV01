from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from .models.news import News
from .models.news_location import NewsLocation

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/news_locations')
def get_news_locations():
    """
    Obtiene las ubicaciones de las noticias con sus datos asociados
    """
    try:
        # Obtener parámetros de filtrado
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Construir la consulta base
        query = NewsLocation.query.join(News)

        # Aplicar filtros de fecha si están presentes
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(News.date >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(News.date <= end_date)

        # Obtener las ubicaciones
        locations = query.all()

        # Formatear los resultados
        locations_data = []
        for loc in locations:
            locations_data.append({
                'id': loc.id,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'location_name': loc.name,
                'title': loc.news.title,
                'description': loc.news.description,
                'url': loc.news.url,
                'date': loc.news.date.strftime('%Y-%m-%d') if loc.news.date else None,
                'country_code': loc.country_code
            })

        return jsonify({
            'status': 'success',
            'locations': locations_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
