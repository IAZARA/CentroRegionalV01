from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.news_service import NewsService
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
