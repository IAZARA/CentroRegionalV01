from app import create_app, db
from app.models.news import News
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
from datetime import datetime, timedelta

# Lista de noticias de ejemplo
sample_news = [
    {
        "title": "Desbaratan una banda narco que operaba en Rosario",
        "content": "La Policía Federal desarticuló una organización criminal dedicada al narcotráfico que operaba en la zona sur de Rosario. Durante los allanamientos se incautaron más de 100 kilos de cocaína.",
        "url": "https://example.com/news1",
        "source": "La Capital"
    },
    {
        "title": "Secuestran drogas en un operativo en La Matanza",
        "content": "Efectivos de la Policía Bonaerense realizaron un importante operativo en La Matanza donde incautaron una gran cantidad de drogas y detuvieron a cinco personas.",
        "url": "https://example.com/news2",
        "source": "Clarín"
    },
    {
        "title": "Detienen a narcotraficantes en el puerto de Buenos Aires",
        "content": "La Prefectura Naval Argentina detuvo a tres personas en el puerto de Buenos Aires cuando intentaban ingresar un cargamento de drogas oculto en contenedores.",
        "url": "https://example.com/news3",
        "source": "Infobae"
    },
    {
        "title": "Operativo antidrogas en Córdoba deja varios detenidos",
        "content": "Un operativo conjunto entre la Policía de Córdoba y la Federal culminó con la detención de 8 personas en diferentes puntos de la ciudad de Córdoba. Se secuestraron drogas y armas.",
        "url": "https://example.com/news4",
        "source": "La Voz"
    },
    {
        "title": "Desarticulan red de narcotráfico en Mendoza",
        "content": "La policía de Mendoza desarticuló una importante red de narcotráfico que operaba en la capital provincial. Se realizaron 12 allanamientos simultáneos.",
        "url": "https://example.com/news5",
        "source": "Los Andes"
    },
    {
        "title": "Incautan cargamento de marihuana en Misiones",
        "content": "Gendarmería Nacional incautó un importante cargamento de marihuana en la provincia de Misiones, cerca de la frontera con Paraguay. El operativo se realizó en la ciudad de Posadas.",
        "url": "https://example.com/news6",
        "source": "El Territorio"
    },
    {
        "title": "Decomisan drogas en el aeropuerto de Ezeiza",
        "content": "Personal de la Policía de Seguridad Aeroportuaria decomisó un cargamento de cocaína en el Aeropuerto Internacional de Ezeiza. La droga estaba oculta en valijas.",
        "url": "https://example.com/news7",
        "source": "Télam"
    },
    {
        "title": "Operativo antidroga en Mar del Plata",
        "content": "La policía realizó varios allanamientos en diferentes puntos de Mar del Plata. Se incautaron drogas y se detuvo a varias personas en el marco de una investigación por narcomenudeo.",
        "url": "https://example.com/news8",
        "source": "La Capital"
    },
    {
        "title": "Desbaratan banda narco en San Miguel de Tucumán",
        "content": "La policía de Tucumán desarticuló una banda dedicada al narcotráfico que operaba en San Miguel de Tucumán. Se realizaron varios allanamientos en la zona.",
        "url": "https://example.com/news9",
        "source": "La Gaceta"
    },
    {
        "title": "Incautan drogas en la Terminal de Retiro",
        "content": "Personal de la Policía Federal realizó un operativo en la Terminal de Retiro, Buenos Aires, donde se incautó un cargamento de drogas que iba a ser trasladado al interior del país.",
        "url": "https://example.com/news10",
        "source": "Clarín"
    },
    {
        "title": "Operativo antidrogas en Quilmes",
        "content": "La policía bonaerense realizó varios allanamientos en Quilmes y desarticuló una banda dedicada al narcomenudeo. Se incautaron drogas y dinero en efectivo.",
        "url": "https://example.com/news11",
        "source": "El Sol"
    },
    {
        "title": "Decomisan cocaína en Santa Fe",
        "content": "En un operativo conjunto entre la policía provincial y federal se decomisaron varios kilos de cocaína en la ciudad de Santa Fe. La droga estaba lista para su distribución.",
        "url": "https://example.com/news12",
        "source": "El Litoral"
    },
    {
        "title": "Detienen narcotraficantes en Salta",
        "content": "La Gendarmería Nacional detuvo a varios narcotraficantes en la provincia de Salta, cerca de la frontera con Bolivia. Se incautó un importante cargamento de drogas.",
        "url": "https://example.com/news13",
        "source": "El Tribuno"
    },
    {
        "title": "Operativo antidroga en La Plata",
        "content": "La policía bonaerense realizó un importante operativo antidroga en La Plata. Se realizaron allanamientos en diferentes puntos de la ciudad y se detuvo a varias personas.",
        "url": "https://example.com/news14",
        "source": "El Día"
    },
    {
        "title": "Desarticulan red narco en Bahía Blanca",
        "content": "Una investigación conjunta entre diferentes fuerzas de seguridad permitió desarticular una red de narcotráfico que operaba en Bahía Blanca y la zona.",
        "url": "https://example.com/news15",
        "source": "La Nueva"
    },
    {
        "title": "Incautan drogas en Neuquén",
        "content": "La policía de Neuquén realizó varios allanamientos en la capital provincial donde se incautaron diferentes tipos de drogas y se detuvo a los responsables.",
        "url": "https://example.com/news16",
        "source": "Río Negro"
    },
    {
        "title": "Operativo antidrogas en San Juan",
        "content": "La policía de San Juan desarticuló una organización dedicada al narcotráfico que operaba en la capital provincial. Se realizaron múltiples allanamientos.",
        "url": "https://example.com/news17",
        "source": "Diario de Cuyo"
    },
    {
        "title": "Decomisan marihuana en Corrientes",
        "content": "Prefectura Naval decomisó un importante cargamento de marihuana en la costa del río Paraná, en la provincia de Corrientes. La droga ingresaba desde Paraguay.",
        "url": "https://example.com/news18",
        "source": "El Litoral"
    },
    {
        "title": "Desbaratan banda narco en Avellaneda",
        "content": "La policía bonaerense desarticuló una banda dedicada al narcotráfico que operaba en Avellaneda. Se realizaron varios allanamientos y se detuvo a los cabecillas.",
        "url": "https://example.com/news19",
        "source": "Clarín"
    },
    {
        "title": "Operativo antidroga en Jujuy",
        "content": "Gendarmería Nacional realizó un importante operativo antidroga en la provincia de Jujuy, cerca de la frontera con Bolivia. Se incautó un cargamento de cocaína.",
        "url": "https://example.com/news20",
        "source": "El Tribuno"
    }
]

def load_sample_news():
    app = create_app()
    with app.app_context():
        # Resetear la base de datos
        db.drop_all()
        db.create_all()
        print("Base de datos reiniciada")
        
        # Crear servicio de geocodificación
        geocoding_service = EnhancedGeocodingService()
        
        # Fecha base para las noticias (30 días atrás)
        base_date = datetime.now() - timedelta(days=30)
        
        # Cargar cada noticia
        for i, news_data in enumerate(sample_news):
            # Crear la noticia con fecha escalonada (1 día de diferencia entre cada una)
            news = News(
                title=news_data['title'],
                content=news_data['content'],
                url=news_data['url'],
                source=news_data['source'],
                published_date=base_date + timedelta(days=i)
            )
            db.session.add(news)
            db.session.commit()
            
            # Procesar ubicaciones
            location = geocoding_service.process_news_item({
                'id': news.id,
                'title': news.title,
                'content': news.content
            })
            
            if location:
                print(f"Ubicación encontrada para noticia {news.id}: {location['name']}")
                geocoding_service.traditional_service.save_location(location, {'id': news.id})
            else:
                print(f"No se encontró ubicación para noticia {news.id}")
                
        print("Noticias de ejemplo cargadas exitosamente")

if __name__ == '__main__':
    load_sample_news()
