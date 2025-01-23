import os
import json
import logging
from typing import Dict, List, Optional
import requests
from app.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.opencage_api_key = os.getenv('OPENCAGE_API_KEY')
        self.cache_file = 'geocoding_cache.json'
        self.cache = self._load_cache()
        self.text_processor = TextProcessor()

    def _load_cache(self) -> Dict:
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando caché: {str(e)}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error guardando caché: {str(e)}")

    def geocode_location(self, location: str) -> Optional[Dict]:
        """
        Geocodifica una ubicación usando OpenCage
        """
        try:
            # Verificar caché
            cache_key = location.lower()
            if cache_key in self.cache:
                logger.info(f"Ubicación encontrada en caché: {location}")
                return self.cache[cache_key]

            # Lista de países conocidos
            known_countries = {
                'Argentina': 'ar',
                'Chile': 'cl',
                'Uruguay': 'uy',
                'Paraguay': 'py',
                'Bolivia': 'bo',
                'Perú': 'pe',
                'Peru': 'pe',
                'Colombia': 'co',
                'Ecuador': 'ec',
                'Venezuela': 've',
                'Brasil': 'br',
                'Mexico': 'mx',
                'México': 'mx'
            }

            # Verificar si la ubicación es un país conocido
            for country, code in known_countries.items():
                if location.lower() == country.lower():
                    # Si es un país, no agregar ", Argentina"
                    search_query = location
                    break
            else:
                # Si no es un país conocido, buscar primero sin país
                search_query = location

            logger.info(f"Búsqueda en OpenCage: {search_query}")
            logger.info(f"OpenCage API Key: {self.opencage_api_key[:5]}...")

            # Hacer la petición a OpenCage
            url = f"https://api.opencagedata.com/geocode/v1/json"
            params = {
                'q': search_query,
                'key': self.opencage_api_key,
                'language': 'es',
                'limit': 1,
                'countrycode': 'ar,cl,uy,py,bo,pe,co,ec,ve,br,mx',  # Limitar a países de interés
                'no_annotations': 1
            }

            response = requests.get(url, params=params)
            data = response.json()

            if not data['results']:
                # Si no hay resultados, intentar con ", Argentina" como fallback
                if search_query != f"{location}, Argentina":
                    return self.geocode_location(f"{location}, Argentina")
                return None

            result = data['results'][0]
            
            # Extraer el código de país del componente correspondiente
            country_code = result['components'].get('country_code', '').lower()
            
            # Si el país no está en nuestra lista de interés, intentar con ", Argentina"
            if country_code not in ['ar', 'cl', 'uy', 'py', 'bo', 'pe', 'co', 'ec', 've', 'br', 'mx']:
                if search_query != f"{location}, Argentina":
                    return self.geocode_location(f"{location}, Argentina")
                return None

            geocoded = {
                'latitude': result['geometry']['lat'],
                'longitude': result['geometry']['lng'],
                'country_code': country_code
            }

            # Guardar en caché
            self.cache[cache_key] = geocoded
            self._save_cache()

            return {
                'lat': geocoded['latitude'],
                'lng': geocoded['longitude'],
                'country_code': geocoded['country_code']
            }

        except Exception as e:
            logger.error(f"Error geocodificando {location}: {str(e)}")
            return None

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
                    
                    if geocoded_data and 'lat' in geocoded_data:
                        # Extraer y validar coordenadas
                        lat = geocoded_data['lat']
                        lng = geocoded_data['lng']
                        
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
                                    'lng': lng,
                                    'country_code': geocoded_data.get('country_code', '').lower()
                                }
                                
                                # Guardar en la base de datos
                                saved_location = self.save_location({
                                    'geometry': {
                                        'lat': lat,
                                        'lng': lng
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
            lng = location_data['geometry'].get('lng')
            
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
