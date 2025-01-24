from app import create_app, db
from app.models.news_location import NewsLocation
from app.models.news import News

app = create_app()

with app.app_context():
    # Contar ubicaciones
    location_count = NewsLocation.query.count()
    print(f"\nTotal de ubicaciones: {location_count}")
    
    if location_count > 0:
        # Mostrar algunas ubicaciones de ejemplo
        print("\nÚltimas 5 ubicaciones:")
        locations = NewsLocation.query.order_by(NewsLocation.created_at.desc()).limit(5).all()
        for loc in locations:
            print(f"\nUbicación: {loc.name}")
            print(f"Coordenadas: ({loc.latitude}, {loc.longitude})")
            print(f"País: {loc.country_code}")
            if loc.news:
                print(f"Noticia: {loc.news.title[:100]}...")
            print("-" * 50)
    
    # Contar noticias
    news_count = News.query.count()
    print(f"\nTotal de noticias: {news_count}")
