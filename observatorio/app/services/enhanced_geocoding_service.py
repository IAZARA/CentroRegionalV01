from typing import List, Dict, Optional
from app.services.geocoding_service import GeocodingService
from app.services.claude_geocoding_service import ClaudeGeocodingService
import logging

logger = logging.getLogger(__name__)

class EnhancedGeocodingService:
    def __init__(self):
        self.traditional_service = GeocodingService()
        self.claude_service = ClaudeGeocodingService()
        
    def process_news_item(self, news_item: Dict) -> List[Dict]:
        """
        Procesa una noticia usando tanto el servicio tradicional como Claude
        y combina los resultados
        """
        try:
            # Obtener ubicaciones usando Claude
            claude_locations = self.claude_service.extract_locations(news_item.get('text', ''))
            
            # Convertir las ubicaciones de Claude al formato necesario
            processed_locations = []
            
            for loc in claude_locations:
                try:
                    # Geocodificar usando el servicio tradicional para obtener coordenadas precisas
                    geocoded = self.traditional_service.geocode_location(loc['name'])
                    
                    if geocoded and 'geometry' in geocoded:
                        processed_locations.append({
                            'name': loc['name'],
                            'latitude': geocoded['geometry'].get('lat'),
                            'longitude': geocoded['geometry'].get('lng'),
                            'country_code': loc.get('country', 'ar')[:2].lower(),
                            'is_primary': loc.get('is_primary', False)
                        })
                except Exception as e:
                    logger.error(f"Error procesando ubicación {loc['name']}: {str(e)}")
                    continue
            
            return processed_locations
            
        except Exception as e:
            logger.error(f"Error en process_news_item: {str(e)}")
            return []

    def extract_locations(self, text: str) -> List[Dict]:
        """
        Extrae ubicaciones del texto usando ambos servicios
        """
        all_locations = {}  # Diccionario para evitar duplicados
        
        try:
            # 1. Intentar primero con Claude
            claude_locations = self.claude_service.extract_locations(text)
            
            for loc in claude_locations:
                try:
                    location_name = loc['name']
                    # Geocodificar usando el servicio tradicional
                    geocoded = self.traditional_service.geocode_location(location_name)
                    
                    if geocoded and 'geometry' in geocoded:
                        # Usar el nombre como clave para evitar duplicados
                        all_locations[location_name] = {
                            'name': location_name,
                            'latitude': geocoded['geometry'].get('lat'),
                            'longitude': geocoded['geometry'].get('lng'),
                            'country_code': loc.get('country', 'ar')[:2].lower(),
                            'is_primary': loc.get('is_primary', False)
                        }
                except Exception as e:
                    logger.error(f"Error procesando ubicación de Claude {loc['name']}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error usando servicio de Claude: {str(e)}")
        
        try:
            # 2. Usar el servicio tradicional como respaldo
            traditional_locations = self.traditional_service.extract_locations(text)
            
            for location_name in traditional_locations:
                if location_name not in all_locations:  # Solo si no fue encontrado por Claude
                    try:
                        geocoded = self.traditional_service.geocode_location(location_name)
                        if geocoded and 'geometry' in geocoded:
                            country_code = self.traditional_service.get_country_code(location_name)
                            all_locations[location_name] = {
                                'name': location_name,
                                'latitude': geocoded['geometry'].get('lat'),
                                'longitude': geocoded['geometry'].get('lng'),
                                'country_code': country_code,
                                'is_primary': False  # El servicio tradicional no detecta ubicación principal
                            }
                    except Exception as e:
                        logger.error(f"Error procesando ubicación tradicional {location_name}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error usando servicio tradicional: {str(e)}")
        
        # Convertir el diccionario en lista
        return list(all_locations.values())
