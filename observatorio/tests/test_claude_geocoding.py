from flask import current_app
from app import create_app
from app.services.enhanced_geocoding_service import EnhancedGeocodingService
import json

def test_claude_geocoding():
    # Crear una instancia de la aplicación
    app = create_app()
    
    # Texto de prueba con varias ubicaciones
    test_text = """
    En Buenos Aires, la capital argentina, se registraron protestas masivas. 
    Los manifestantes marcharon desde el Obelisco hasta la Plaza de Mayo.
    Mientras tanto, en Rosario, Santa Fe, se reportaron incidentes similares.
    La situación también afectó a otras ciudades como Córdoba y Mendoza.
    En Chile, específicamente en Santiago, hubo manifestaciones de apoyo.
    """
    
    with app.app_context():
        # Crear instancia del servicio
        geocoding_service = EnhancedGeocodingService()
        
        # Extraer ubicaciones
        locations = geocoding_service.extract_locations(test_text)
        
        # Imprimir resultados
        print("\n🌍 Ubicaciones encontradas:")
        print(json.dumps(locations, indent=2, ensure_ascii=False))
        
        # Verificar resultados
        if locations:
            print("\n✅ Se encontraron las siguientes ubicaciones:")
            for loc in locations:
                print(f"📍 {loc['name']}")
                print(f"   País: {loc['country_code']}")
                print(f"   Coordenadas: {loc['latitude']}, {loc['longitude']}")
                print(f"   Principal: {'Sí' if loc['is_primary'] else 'No'}")
                print()
        else:
            print("\n❌ No se encontraron ubicaciones")

if __name__ == '__main__':
    test_claude_geocoding()
