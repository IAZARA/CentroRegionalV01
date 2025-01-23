from app import create_app
from app.models import News
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Obtener el total de noticias
    total_news = News.query.count()
    
    # Obtener noticias de las últimas 24 horas
    yesterday = datetime.now() - timedelta(days=1)
    recent_news = News.query.filter(News.created_at >= yesterday).all()
    
    print(f"\nTotal de noticias en la base de datos: {total_news}")
    print(f"Noticias agregadas en las últimas 24 horas: {len(recent_news)}\n")
    
    if recent_news:
        print("Últimas noticias agregadas:")
        print("-" * 80)
        for item in recent_news:
            print(f"Título: {item.title}")
            print(f"Fuente: {item.source}")
            print(f"País: {item.country}")
            print(f"Palabras clave: {item.keywords}")
            print(f"Fecha de publicación: {item.published_date}")
            print(f"Fecha de creación: {item.created_at}")
            print(f"URL: {item.url}")
            print("-" * 80)
    else:
        print("No se han agregado noticias en las últimas 24 horas.")
