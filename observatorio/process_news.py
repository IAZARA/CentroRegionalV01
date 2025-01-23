from app import create_app
from app.tasks import process_existing_news
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

app = create_app()
with app.app_context():
    print("Iniciando procesamiento de noticias...")
    process_existing_news()
