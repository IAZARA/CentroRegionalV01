import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///observatorio.db'  # Forzar SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    
    # Mapbox
    MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
    
    # OpenCage Geocoding
    OPENCAGE_API_KEY = os.environ.get('OPENCAGE_API_KEY')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Babel
    LANGUAGES = ['es', 'en', 'pt']
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_TRANSLATION_DIRECTORIES = '../translations'
    
    # Dominios por país
    COUNTRY_DOMAINS = {
        '.ar': {
            'name': 'Argentina',
            'domains': ['clarin.com', 'lanacion.com.ar', 'infobae.com', 'pagina12.com.ar', 'telam.com.ar']
        },
        '.cl': {
            'name': 'Chile',
            'domains': ['emol.com', 'latercera.com', 'cooperativa.cl', 'elmostrador.cl']
        },
        '.uy': {
            'name': 'Uruguay',
            'domains': ['elpais.com.uy', 'elobservador.com.uy', 'montevideo.com.uy']
        },
        '.py': {
            'name': 'Paraguay',
            'domains': ['abc.com.py', 'ultimahora.com', 'lanacion.com.py']
        },
        '.bo': {
            'name': 'Bolivia',
            'domains': ['eldeber.com.bo', 'la-razon.com', 'lostiempos.com']
        }
    }
