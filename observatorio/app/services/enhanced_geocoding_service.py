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
        
        # Lista de países de América
        self.america_countries = {
            'argentina': 'ar',
            'bolivia': 'bo',
            'brasil': 'br',
            'chile': 'cl',
            'colombia': 'co',
            'ecuador': 'ec',
            'guyana': 'gy',
            'paraguay': 'py',
            'peru': 'pe',
            'surinam': 'sr',
            'uruguay': 'uy',
            'venezuela': 've',
            'mexico': 'mx',
            'belice': 'bz',
            'costa rica': 'cr',
            'el salvador': 'sv',
            'guatemala': 'gt',
            'honduras': 'hn',
            'nicaragua': 'ni',
            'panama': 'pa',
            'cuba': 'cu',
            'haiti': 'ht',
            'republica dominicana': 'do',
            'estados unidos': 'us',
            'canada': 'ca'
        }

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesa una noticia para extraer y geocodificar su ubicación principal
        """
        try:
            # Combinar título y contenido para análisis
            text = f"{news_item.get('title', '')} {news_item.get('content', '')}"
            
            # Extraer ubicaciones usando el servicio de IA
            locations = self.ai_service.extract_locations(text)
            
            if not locations:
                logger.info(f"No se encontraron ubicaciones en la noticia ID: {news_item.get('id')}")
                return None
            
            # Ordenar ubicaciones por relevancia
            # 1. Ubicaciones en el título tienen prioridad
            # 2. Ubicaciones que aparecen primero en el texto
            title = news_item.get('title', '').lower()
            for loc in locations:
                loc['score'] = 0
                if loc['name'].lower() in title:
                    loc['score'] += 10
                if loc.get('is_primary', False):
                    loc['score'] += 5
            
            # Ordenar por score y seleccionar la ubicación con mayor puntaje
            locations.sort(key=lambda x: x['score'], reverse=True)
            primary_location = locations[0]
            
            # Geocodificar la ubicación principal
            geocoded = self.geocode_location(primary_location)
            if not geocoded:
                return None
                
            return {
                'name': primary_location['name'],
                'latitude': geocoded['latitude'],
                'longitude': geocoded['longitude'],
                'country_code': geocoded.get('country_code', 'ar'),
                'is_primary': True
            }
            
        except Exception as e:
            logger.error(f"Error procesando noticia {news_item.get('id')}: {str(e)}")
            return None

    def geocode_location(self, location: Dict) -> Optional[Dict]:
        """
        Geocodifica una ubicación en América
        """
        try:
            # Obtener el contexto completo de la ubicación
            location_parts = []
            if location.get('name'):
                location_parts.append(location['name'])
            if location.get('state'):
                location_parts.append(location['state'])
            if location.get('country'):
                location_parts.append(location['country'])
            
            # Crear query de búsqueda con el contexto completo
            search_query = ", ".join(location_parts)
            
            # Intentar geocodificar
            result = self.traditional_service.geocode_location(search_query)
            logger.info(f"Resultado de geocodificación para {search_query}: {result}")
            
            if result and 'geometry' in result:
                # Extraer lat/lon del resultado
                lat = result['geometry'].get('lat')
                lon = result['geometry'].get('lon') or result['geometry'].get('lng')
                logger.info(f"Coordenadas encontradas para {search_query}: lat={lat}, lon={lon}")
                
                if lat is not None and lon is not None:
                    # Verificar si el país está en América
                    country_code = result.get('country_code', '').lower()
                    if country_code in self.america_countries.values():
                        return {
                            'name': search_query,
                            'latitude': lat,
                            'longitude': lon,
                            'country_code': country_code,
                            'is_primary': location.get('is_primary', False),
                            'type': location.get('type', 'unknown')
                        }
                    else:
                        logger.warning(f"La ubicación {search_query} no está en América: {country_code}")
                else:
                    logger.warning(f"Coordenadas inválidas para {search_query}: lat={lat}, lon={lon}")
            else:
                logger.warning(f"No se encontró geometría para {search_query}")
                
            return None
                
        except Exception as e:
            logger.error(f"Error al geocodificar {location.get('name', 'unknown')}: {str(e)}")
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
                    
                    # Solo procesar ubicaciones de América
                    if loc.get('type') == 'country' and loc.get('name') not in self.america_countries:
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
