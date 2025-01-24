from typing import List, Dict, Optional
from .geocoding_service import GeocodingService
from .anthropic_service import AnthropicService
import logging
import re

logger = logging.getLogger(__name__)

class EnhancedGeocodingService:
    def __init__(self):
        self.traditional_service = GeocodingService()
        self.ai_service = AnthropicService()
        
        # Lista de provincias argentinas y sus capitales
        self.argentina_locations = {
            'buenos aires': 'ar',
            'ciudad autónoma de buenos aires': 'ar',
            'córdoba': 'ar',
            'santa fe': 'ar',
            'mendoza': 'ar',
            'tucumán': 'ar',
            'entre ríos': 'ar',
            'salta': 'ar',
            'misiones': 'ar',
            'chaco': 'ar',
            'corrientes': 'ar',
            'santiago del estero': 'ar',
            'san juan': 'ar',
            'jujuy': 'ar',
            'río negro': 'ar',
            'neuquén': 'ar',
            'formosa': 'ar',
            'chubut': 'ar',
            'san luis': 'ar',
            'la pampa': 'ar',
            'catamarca': 'ar',
            'la rioja': 'ar',
            'santa cruz': 'ar',
            'tierra del fuego': 'ar',
            # Ciudades importantes
            'mar del plata': 'ar',
            'rosario': 'ar',
            'la plata': 'ar',
            'san miguel de tucumán': 'ar',
            'salta': 'ar',
            'santa fe': 'ar',
            'san juan': 'ar',
            'resistencia': 'ar',
            'neuquén': 'ar',
            'bariloche': 'ar',
            'bahía blanca': 'ar'
        }

    def process_news_item(self, news_item: Dict) -> List[Dict]:
        """
        Procesa una noticia usando tanto el servicio tradicional como Claude
        y combina los resultados
        """
        try:
            # Obtener ubicaciones usando Claude
            claude_locations = self.ai_service.extract_locations(news_item.get('text', ''))
            
            # Convertir las ubicaciones de Claude al formato necesario
            processed_locations = []
            
            for loc in claude_locations:
                try:
                    # Geocodificar usando el servicio tradicional para obtener coordenadas precisas
                    geocoded = self.geocode_location(loc)
                    
                    if geocoded:
                        processed_locations.append(geocoded)
                except Exception as e:
                    logger.error(f"Error procesando ubicación {loc['name']}: {str(e)}")
                    continue
            
            return processed_locations
            
        except Exception as e:
            logger.error(f"Error en process_news_item: {str(e)}")
            return []

    def geocode_location(self, location: Dict) -> Optional[Dict]:
        """
        Geocodifica una ubicación y verifica que sea de Argentina
        """
        try:
            # Asegurarse de que la búsqueda sea específica para Argentina
            search_query = f"{location['name']}, Argentina"
            
            # Intentar geocodificar
            result = self.traditional_service.geocode_location(search_query)
            logger.info(f"Resultado de geocodificación para {location['name']}: {result}")
            
            if result and 'geometry' in result:
                # Extraer lat/lon del resultado
                lat = result['geometry'].get('lat')
                # Intentar obtener la longitud como 'lon' o 'lng'
                lon = result['geometry'].get('lon') or result['geometry'].get('lng')
                logger.info(f"Coordenadas encontradas para {location['name']}: lat={lat}, lon={lon}")
                
                if lat is not None and lon is not None:
                    return {
                        'name': location['name'],
                        'latitude': lat,
                        'longitude': lon,
                        'country_code': result.get('country_code', 'ar'),
                        'is_primary': location.get('is_primary', False),
                        'type': location.get('type', 'unknown')
                    }
                else:
                    logger.warning(f"Coordenadas inválidas para {location['name']}: lat={lat}, lon={lon}")
            else:
                logger.warning(f"No se encontró geometría para {location['name']}")
                
            logger.warning(f"La ubicación {location['name']} no se pudo geocodificar")
            return None
                
        except Exception as e:
            logger.error(f"Error al geocodificar {location['name']}: {str(e)}")
            return None
            
    def extract_locations(self, text: str) -> List[Dict]:
        """
        Extrae ubicaciones del texto usando una combinación de servicios
        """
        try:
            # Primero usamos el servicio de IA para identificar posibles ubicaciones
            ai_locations = self.ai_service.extract_locations(text)
            logger.info(f"Ubicaciones identificadas por IA: {ai_locations}")
            
            # Lista para almacenar las ubicaciones geocodificadas
            geocoded_locations = []
            
            # Procesar cada ubicación encontrada por la IA
            for loc in ai_locations:
                try:
                    location_name = loc['name']
                    
                    # Solo procesar ubicaciones de Argentina
                    if loc.get('type') == 'country' and loc.get('name') != 'Argentina':
                        continue
                        
                    geocoded = self.geocode_location(loc)
                    if geocoded:
                        geocoded_locations.append(geocoded)
                except Exception as e:
                    logger.error(f"Error procesando ubicación {loc['name']}: {str(e)}")
                    continue
            
            return geocoded_locations
            
        except Exception as e:
            logger.error(f"Error en extract_locations: {str(e)}")
            return []
