import os
import json
import logging
from typing import Dict, List, Optional
import requests
from app.utils.text_processor import TextProcessor
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        """
        Inicializa el servicio de geocodificación
        """
        self.opencage_api_key = os.environ.get('OPENCAGE_API_KEY')
        self.cache_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'geocoding_cache.json')
        self.cache = self._load_cache()
        
        # Coordenadas de provincias y ciudades importantes de Argentina
        self.argentina_provinces = {
            'mar del plata': {
                'lat': -38.0055,
                'lon': -57.5426
            },
            'buenos aires': {
                'lat': -34.6037,
                'lon': -58.3816
            },
            'cordoba': {
                'lat': -31.4201,
                'lon': -64.1888
            },
            'rosario': {
                'lat': -32.9468,
                'lon': -60.6393
            },
            'mendoza': {
                'lat': -32.8908,
                'lon': -68.8272
            },
            'la plata': {
                'lat': -34.9205,
                'lon': -57.9536
            },
            'san miguel de tucuman': {
                'lat': -26.8241,
                'lon': -65.2226
            },
            'salta': {
                'lat': -24.7829,
                'lon': -65.4232
            },
            'santa fe': {
                'lat': -31.6107,
                'lon': -60.6973
            },
            'corrientes': {
                'lat': -27.4692,
                'lon': -58.8306
            },
            'resistencia': {
                'lat': -27.4510,
                'lon': -58.9868
            },
            'posadas': {
                'lat': -27.3621,
                'lon': -55.9007
            },
            'parana': {
                'lat': -31.7413,
                'lon': -60.5115
            },
            'neuquen': {
                'lat': -38.9516,
                'lon': -68.0591
            },
            'formosa': {
                'lat': -26.1775,
                'lon': -58.1781
            },
            'san salvador de jujuy': {
                'lat': -24.1858,
                'lon': -65.2995
            },
            'san luis': {
                'lat': -33.3022,
                'lon': -66.3376
            },
            'san juan': {
                'lat': -31.5375,
                'lon': -68.5364
            },
            'rio gallegos': {
                'lat': -51.6230,
                'lon': -69.2168
            },
            'ushuaia': {
                'lat': -54.8019,
                'lon': -68.3030
            },
            'rawson': {
                'lat': -43.3001,
                'lon': -65.1023
            },
            'viedma': {
                'lat': -40.8135,
                'lon': -62.9967
            },
            'santa rosa': {
                'lat': -36.6167,
                'lon': -64.2833
            },
            'rio cuarto': {
                'lat': -33.1307,
                'lon': -64.3499
            }
        }

    def _load_cache(self) -> Dict:
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando caché: {str(e)}")
        return {}

    def _save_cache(self):
        """
        Guarda el caché en un archivo JSON
        """
        try:
            # Asegurarse de que el directorio data existe
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando caché: {str(e)}")

    def _clean_location_name(self, name: str) -> str:
        """
        Limpia y normaliza el nombre de una ubicación
        """
        # Convertir a minúsculas y quitar espacios extras
        clean = name.lower().strip()
        
        # Quitar acentos
        clean = clean.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        
        # Quitar caracteres especiales
        clean = re.sub(r'[^a-z\s]', '', clean)
        
        # Quitar espacios múltiples
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()

    def get_country_code(self, location: str) -> str:
        """
        Obtener el código de país para una ubicación
        """
        try:
            geocoded = self.geocode_location(location)
            if geocoded and 'country_code' in geocoded:
                return geocoded['country_code']
            return 'ar'  # default a Argentina si no se encuentra
        except Exception as e:
            logger.error(f"Error obteniendo código de país para {location}: {str(e)}")
            return 'ar'

    def extract_locations(self, text: str) -> List[str]:
        """
        Extrae ubicaciones de un texto usando el procesador de texto
        """
        try:
            # Usar el procesador de texto para extraer ubicaciones
            locations = self.text_processor.extract_locations(text)
            return list(set(locations))  # Eliminar duplicados
        except Exception as e:
            logger.error(f"Error extrayendo ubicaciones: {str(e)}")
            return []

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesa una noticia para extraer y geocodificar sus ubicaciones
        """
        try:
            if not news_item or 'text' not in news_item:
                return None
                
            text = news_item['text']
            locations = self.extract_locations(text)
            logger.info(f"Ubicaciones encontradas: {locations}")
            
            processed_locations = []
            for location in locations:
                try:
                    # Geocodificar la ubicación
                    geocoded_data = self.geocode_location(location)
                    
                    if geocoded_data and 'geometry' in geocoded_data:
                        # Extraer y validar coordenadas
                        lat = geocoded_data['geometry']['lat']
                        lng = geocoded_data['geometry']['lon']
                        
                        if lat is not None and lng is not None:
                            try:
                                # Convertir a float y validar rangos
                                lat = float(lat)
                                lng = float(lng)
                                
                                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                                    logger.warning(f"Coordenadas fuera de rango para {location}: lat={lat}, lng={lng}")
                                    continue
                                    
                                # Redondear a 6 decimales
                                lat = round(lat, 6)
                                lng = round(lng, 6)
                                
                                # Crear objeto de ubicación procesada
                                processed_location = {
                                    'name': location,
                                    'lat': lat,
                                    'lon': lng,
                                    'country_code': geocoded_data.get('country_code', '').lower()
                                }
                                
                                # Guardar en la base de datos
                                saved_location = self.save_location({
                                    'geometry': {
                                        'lat': lat,
                                        'lon': lng
                                    },
                                    'components': {
                                        'country_code': processed_location['country_code']
                                    }
                                }, {
                                    'id': news_item['id'],
                                    'location': location
                                })
                                
                                if saved_location:
                                    processed_locations.append(processed_location)
                                    logger.info(f"Ubicación procesada exitosamente: {location} ({lat}, {lng})")
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error al procesar coordenadas para {location}: {str(e)}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error procesando ubicación {location}: {str(e)}")
                    continue
            
            if processed_locations:
                return {
                    'news_id': news_item['id'],
                    'locations': processed_locations
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error procesando noticia {news_item.get('id')}: {str(e)}")
            return None

    def save_location(self, location_data: Dict, news_item: Dict) -> Optional[Dict]:
        """
        Guarda una ubicación en la base de datos
        """
        try:
            if not location_data or 'geometry' not in location_data:
                return None
                
            # Extraer y validar las coordenadas
            lat = location_data['geometry'].get('lat')
            lng = location_data['geometry'].get('lon')
            
            # Validar que lat y lng sean números y estén en rangos válidos
            try:
                lat = float(lat)
                lng = float(lng)
                
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    logger.warning(f"Coordenadas fuera de rango: lat={lat}, lng={lng}")
                    return None
                    
                # Redondear a 6 decimales
                lat = round(lat, 6)
                lng = round(lng, 6)
                
            except (TypeError, ValueError) as e:
                logger.warning(f"Error al convertir coordenadas: {str(e)}")
                return None
            
            # Crear o actualizar la ubicación
            location = NewsLocation.query.filter_by(
                news_id=news_item['id'],
                name=news_item.get('location', ''),
                latitude=lat,
                longitude=lng
            ).first()
            
            if not location:
                location = NewsLocation(
                    news_id=news_item['id'],
                    name=news_item.get('location', ''),
                    latitude=lat,
                    longitude=lng,
                    country_code=location_data.get('components', {}).get('country_code', '').lower()
                )
                db.session.add(location)
            
            db.session.commit()
            
            return {
                'id': location.id,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'country_code': location.country_code
            }
            
        except Exception as e:
            logger.error(f"Error al guardar ubicación: {str(e)}")
            db.session.rollback()
            return None

    def _get_source(self, news_item: Dict) -> str:
        """
        Determina la fuente de la noticia basada en su URL
        """
        try:
            url = news_item.get('link', '')
            domain = urlparse(url).netloc.lower()
            domain = re.sub(r'^www\.', '', domain)
            
            # Mapeo de dominios conocidos
            source_map = {
                'infobae.com': 'Infobae',
                'clarin.com': 'Clarín',
                'lanacion.com.ar': 'La Nación',
                'emol.com': 'Emol',
                'cooperativa.cl': 'Cooperativa',
                'abc.com.py': 'ABC Color'
            }
            
            for known_domain, source in source_map.items():
                if known_domain in domain:
                    return source
                    
            return domain.split('.')[0].capitalize()
            
        except Exception:
            return 'Internacional'

    def _determine_category(self, news_item: Dict) -> str:
        """
        Determina la categoría de la noticia basada en su contenido
        """
        categories = {
            'Narcotráfico': ['droga', 'cocaína', 'marihuana', 'narcotráfico', 'cartel'],
            'Violencia': ['homicidio', 'asesinato', 'violencia', 'crimen'],
            'Corrupción': ['corrupción', 'soborno', 'lavado de dinero'],
            'Trata': ['trata de personas', 'tráfico de personas', 'explotación']
        }
        
        text = f"{news_item.get('title', '')} {news_item.get('description', '')}".lower()
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        return 'Internacional'

    @lru_cache(maxsize=1000)
    def geocode_location(self, location: str) -> Optional[Dict]:
        """
        Geocodifica una ubicación usando OpenCage o el diccionario de ubicaciones conocidas
        """
        try:
            # Verificar cache
            cache_key = location.lower().strip()
            if cache_key in self.cache:
                logger.info(f"Ubicación encontrada en caché: {location}")
                return self.cache[cache_key]
            
            # Verificar si es una provincia o ciudad argentina conocida
            clean_name = self._clean_location_name(location)
            if clean_name in self.argentina_provinces:
                coords = self.argentina_provinces[clean_name]
                result = {
                    'name': location,
                    'geometry': {
                        'lat': coords['lat'],
                        'lon': coords['lon']
                    },
                    'components': {
                        'country_code': 'ar'
                    },
                    'country_code': 'ar'
                }
                self.cache[cache_key] = result
                self._save_cache()
                return result
            
            # Si no está en el diccionario, usar OpenCage
            url = f'https://api.opencagedata.com/geocode/v1/json'
            params = {
                'q': location,
                'key': self.opencage_api_key,
                'countrycode': 'ar',  # Limitar a Argentina
                'language': 'es',     # Resultados en español
                'limit': 1           # Solo el primer resultado
            }
            
            logger.info(f"Búsqueda en OpenCage: {location}")
            logger.info(f"OpenCage API Key: {self.opencage_api_key[:5]}...")
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['results']:
                result = data['results'][0]
                if result['components'].get('country_code') == 'ar':
                    formatted_result = {
                        'name': location,
                        'geometry': {
                            'lat': result['geometry']['lat'],
                            'lon': result['geometry']['lng']
                        },
                        'components': {
                            'country_code': 'ar'
                        },
                        'country_code': 'ar'
                    }
                    self.cache[cache_key] = formatted_result
                    self._save_cache()
                    return formatted_result
            
            return None
            
        except Exception as e:
            logger.error(f"Error geocodificando {location}: {str(e)}")
            return None

    def clear_cache(self, location: str = None):
        """
        Limpia el caché de geocodificación. Si se especifica una ubicación,
        solo limpia esa entrada.
        """
        if location:
            cache_key = location.lower().strip()
            if cache_key in self.cache:
                del self.cache[cache_key]
                logger.info(f"Limpiada entrada de caché para: {location}")
        else:
            self.cache.clear()
            logger.info("Caché limpiado completamente")
        self._save_cache()
