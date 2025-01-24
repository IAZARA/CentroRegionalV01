import os

class DevelopmentConfig:
    # Configuración de Flask
    SECRET_KEY = 'dev-key-12345'
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/observatorio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de paginación
    POSTS_PER_PAGE = 10

    # Configuración de Celery
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Configuración de APIs
    MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCvxpQAB-wBAqe25KrBdIelktXrT26IPs4')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', 'c7187cfce45fa4986')
    OPENCAGE_API_KEY = os.environ.get('OPENCAGE_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Configuración de Flask-Login
    LOGIN_DISABLED = False
    LOGIN_VIEW = 'auth.login'
    USE_SESSION_FOR_NEXT = True
