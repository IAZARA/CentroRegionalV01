import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    
    # Configuración de la base de datos
    # Usar SQLite con una ubicación específica para almacenar los datos de los usuarios
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'observatorio.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de paginación
    POSTS_PER_PAGE = 10

    # Configuración de Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Configuración de Apify
    APIFY_API_TOKEN = os.environ.get('APIFY_API_TOKEN')

    # Configuración de dominios de búsqueda
    COUNTRY_DOMAINS = {
        '.ar': {'name': 'Argentina', 'domains': ['clarin.com', 'lanacion.com.ar', 'infobae.com', 'pagina12.com.ar']},
        '.cl': {'name': 'Chile', 'domains': ['emol.com', 'latercera.com', 'elmostrador.cl']},
        '.uy': {'name': 'Uruguay', 'domains': ['elpais.com.uy', 'elobservador.com.uy', 'montevideo.com.uy']},
        '.py': {'name': 'Paraguay', 'domains': ['abc.com.py', 'ultimahora.com', 'lanacion.com.py']},
        '.bo': {'name': 'Bolivia', 'domains': ['eldeber.com.bo', 'paginasiete.bo', 'la-razon.com']},
    }

    # Configuración de Flask-Login
    LOGIN_DISABLED = False
    LOGIN_VIEW = 'auth.login'
    USE_SESSION_FOR_NEXT = True
    
    # Configuración de Flask-Babel
    LANGUAGES = ['es', 'en', 'pt']
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
