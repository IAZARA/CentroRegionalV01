from app import create_app
from app.services.geocoding_service import GeocodingService

app = create_app()

with app.app_context():
    geocoding_service = GeocodingService()
    
    # Texto de prueba
    text = "La operación se llevó a cabo en la ciudad de Buenos Aires, cerca de la estación de Retiro"
    
    # Extraer ubicaciones
    locations = geocoding_service.extract_locations(text)
    print(f"Ubicaciones encontradas: {locations}")
    
    # Geocodificar cada ubicación
    for location in locations:
        coords = geocoding_service.geocode_location(location)
        print(f"Coordenadas para {location}: {coords}")
