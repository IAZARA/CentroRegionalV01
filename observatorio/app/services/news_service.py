# Este servicio ha sido deshabilitado tras la migración a iFrames de Looker Pro.
# El procesamiento de noticias ahora se realiza directamente en Looker Pro.
# Se mantiene el archivo para referencia histórica.

import logging

logger = logging.getLogger(__name__)

class NewsService:
    """
    SERVICIO DESHABILITADO - Migrado a Looker Pro
    
    Este servicio anteriormente utilizaba Google Custom Search API para buscar
    y procesar noticias relacionadas con drogas sintéticas. Tras la migración
    a iFrames de Looker Pro, esta funcionalidad ya no es necesaria.
    """
    
    def __init__(self):
        logger.warning("NewsService está deshabilitado tras la migración a Looker Pro")
        pass

    def search_news(self, *args, **kwargs):
        """Método deshabilitado - usar Looker Pro"""
        logger.warning("search_news() está deshabilitado - usar Looker Pro")
        return []

    def get_news_stats(self):
        """Método deshabilitado - usar Looker Pro"""
        logger.warning("get_news_stats() está deshabilitado - usar Looker Pro")
        return {'total': 0, 'countries': {}, 'news_last_24h': 0}

def get_news():
    """
    Función auxiliar deshabilitada - usar Looker Pro
    """
    logger.warning("get_news() está deshabilitado - usar Looker Pro")
    return []
