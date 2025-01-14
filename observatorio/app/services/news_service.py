import requests
from datetime import datetime, timedelta
from flask import current_app
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = current_app.config['GOOGLE_API_KEY']
        self.search_engine_id = current_app.config['GOOGLE_SEARCH_ENGINE_ID']
        self.country_domains = current_app.config['COUNTRY_DOMAINS']

    def search_news(self, keywords=None, country=None, days=7):
        """
        Busca noticias usando Google Custom Search API.
        
        Args:
            keywords (list): Lista de palabras clave para buscar
            country (str): Código de país para filtrar (.ar, .cl, etc.)
            days (int): Número de días hacia atrás para buscar
            
        Returns:
            list: Lista de noticias encontradas
        """
        if not keywords:
            keywords = ["drogas sintéticas", "narcotráfico", "metanfetamina", "éxtasis", "mdma"]

        all_news = []
        domains = []

        # Si se especifica un país, usar solo los dominios de ese país
        if country and country in self.country_domains:
            domains.extend(self.country_domains[country]['domains'])
        else:
            # Si no se especifica país, usar todos los dominios
            for country_info in self.country_domains.values():
                domains.extend(country_info['domains'])

        # Crear la restricción de sitios
        site_restrict = ' OR '.join(f'site:{domain}' for domain in domains)

        for keyword in keywords:
            try:
                formatted_query = f'{keyword} ({site_restrict})'
                response = requests.get(
                    'https://www.googleapis.com/customsearch/v1',
                    params={
                        'key': self.api_key,
                        'cx': self.search_engine_id,
                        'q': formatted_query,
                        'dateRestrict': f'd{days}',
                        'num': 10,
                        'sort': 'date:r'
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f'Error en la búsqueda de Google: {response.status_code}')
                    continue

                data = response.json()
                if 'items' not in data:
                    continue

                for item in data['items']:
                    # Extraer el dominio de la URL
                    domain = urlparse(item['link']).netloc
                    
                    # Encontrar el país correspondiente al dominio
                    country_code = None
                    for code, info in self.country_domains.items():
                        if any(d in domain for d in info['domains']):
                            country_code = code
                            break

                    news_item = {
                        'title': item.get('title'),
                        'link': item.get('link'),
                        'snippet': item.get('snippet'),
                        'source': domain,
                        'country': country_code,
                        'keyword': keyword,
                        'published_date': datetime.now()  # Google no proporciona la fecha directamente
                    }
                    all_news.append(news_item)

            except Exception as e:
                logger.error(f'Error al buscar noticias para {keyword}: {str(e)}')
                continue

        return all_news

    def get_news_stats(self):
        """
        Obtiene estadísticas de las noticias.
        
        Returns:
            dict: Estadísticas de noticias
        """
        news = self.search_news()
        
        # Contar noticias por país
        countries = {}
        for country_code, info in self.country_domains.items():
            count = len([n for n in news if n['country'] == country_code])
            countries[country_code] = {
                'name': info['name'],
                'count': count
            }

        # Contar noticias en las últimas 24 horas
        news_last_24h = len([
            n for n in news 
            if n['published_date'] >= datetime.now() - timedelta(days=1)
        ])

        return {
            'total': len(news),
            'countries': countries,
            'news_last_24h': news_last_24h
        }

def get_news():
    """
    Función auxiliar para obtener noticias.
    """
    service = NewsService()
    return service.search_news()
