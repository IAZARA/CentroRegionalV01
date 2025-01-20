import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from flask import current_app
from datetime import datetime
import json
import os
from app.models.news_location import NewsLocation
from app import db

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.opencage_api_key = current_app.config['OPENCAGE_API_KEY']
        self.country_domains = current_app.config['COUNTRY_DOMAINS']
        self.cache_file = 'geocoding_cache.json'
        self._load_cache()

    def _load_cache(self):
        """Cargar caché de geocodificación desde archivo"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.error(f"Error loading geocoding cache: {str(e)}")
            self.cache = {}

    def _save_cache(self):
        """Guardar caché de geocodificación a archivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving geocoding cache: {str(e)}")

    def extract_locations(self, text: str) -> List[str]:
        """
        Extraer posibles ubicaciones del texto usando patrones comunes
        """
        # Lista de palabras a ignorar (reducida y más específica)
        ignore_words = {
            'pesos', 'millones', 'drogas', 'manera', 'sector', 'policía',
            'gobierno', 'estado'
        }
        
        # Patrones de ubicación más flexibles
        patterns = [
            # Ciudades y lugares después de preposiciones
            r'(?:en|desde|de|cerca de|hacia|para|sobre) (?:la ciudad de |el municipio de |la localidad de )?([A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)*)',
            # Nombres propios que parecen ubicaciones
            r'(?<![a-záéíóúñ])[A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*(?![a-záéíóúñ])',
            # Referencias geográficas específicas
            r'(?:puerto|ciudad|provincia|estado|región|departamento|municipio) (?:de |del |de la )?([A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)*)'
        ]

        locations = []
        
        # Buscar en el texto original para mantener las mayúsculas
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.UNICODE | re.IGNORECASE)
            for match in matches:
                # Tomar el grupo capturado si existe, sino tomar todo el match
                location = match.group(1) if match.groups() else match.group(0)
                location = location.strip()
                
                # Validar la ubicación
                location_lower = location.lower()
                if (len(location) > 2 and  # Más de 2 caracteres
                    not any(word in location_lower for word in ignore_words) and  # No contiene palabras a ignorar
                    not re.match(r'\d', location) and  # No empieza con número
                    not location.isupper()):  # No es todo mayúsculas
                    locations.append(location)

        # Eliminar duplicados preservando el orden
        return list(dict.fromkeys(locations))

    def get_country_from_url(self, url: str) -> Optional[str]:
        """
        Obtener código de país desde la URL de la noticia o su contenido
        """
        # Mapeo de dominios específicos a países
        domain_country_map = {
            'infobae.com': 'ar',
            'clarin.com': 'ar',
            'lanacion.com.ar': 'ar',
            'pagina12.com.ar': 'ar',
            'emol.com': 'cl',
            'latercera.com': 'cl',
            'elmostrador.cl': 'cl',
            'elpais.com.uy': 'uy',
            'elobservador.com.uy': 'uy',
            'montevideo.com.uy': 'uy',
            'abc.com.py': 'py',
            'ultimahora.com': 'py',
            'lanacion.com.py': 'py',
            'eldeber.com.bo': 'bo',
            'paginasiete.bo': 'bo',
            'la-razon.com': 'bo'
        }

        try:
            domain = urlparse(url).netloc.lower()
            # Eliminar 'www.' si existe
            domain = re.sub(r'^www\.', '', domain)
            
            # Buscar en el mapeo de dominios
            for known_domain, country in domain_country_map.items():
                if known_domain in domain:
                    return country
                    
            # Si no se encuentra en el mapeo, intentar extraer del TLD
            tld = domain.split('.')[-1].lower()
            if tld in ['ar', 'cl', 'uy', 'py', 'bo']:
                return tld
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting country from URL {url}: {str(e)}")
            return None

    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Geocodificar una ubicación usando OpenCage Geocoding API
        """
        cache_key = f"{location}"
        
        # Verificar caché
        if cache_key in self.cache:
            return self.cache[cache_key].get('coordinates')

        try:
            # Mapeo de países y sus coordenadas aproximadas de centro
            country_bounds = {
                'ar': {'min_lat': -55, 'max_lat': -22, 'min_lng': -73, 'max_lng': -53},
                'cl': {'min_lat': -56, 'max_lat': -17, 'min_lng': -76, 'max_lng': -66},
                'uy': {'min_lat': -35, 'max_lat': -30, 'min_lng': -58, 'max_lng': -53},
                'py': {'min_lat': -27, 'max_lat': -19, 'min_lng': -62, 'max_lng': -54},
                'bo': {'min_lat': -23, 'max_lat': -9, 'min_lng': -69, 'max_lng': -57}
            }

            # Agregar el nombre del país a la búsqueda
            country_names = {
                'ar': 'Argentina',
                'cl': 'Chile',
                'uy': 'Uruguay',
                'py': 'Paraguay',
                'bo': 'Bolivia'
            }
            
            country_code = self._get_country_code(location)
            country_name = country_names.get(country_code.lower())
            if not country_name:
                return None

            # Limpiar y preparar la ubicación
            location = re.sub(r'^(?:ciudad|provincia|estado|región|departamento|municipio)(?:\s+(?:de|del|de la))?\s+', '', location, flags=re.IGNORECASE)
            search_query = f"{location}, {country_name}"
            
            response = requests.get(
                'https://api.opencagedata.com/geocode/v1/json',
                params={
                    'q': search_query,
                    'key': self.opencage_api_key,
                    'limit': 1,
                    'countrycode': country_code,
                    'no_annotations': 1,
                    'no_record': 1,
                    'language': 'es'
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    result = data['results'][0]
                    
                    # Reducir el umbral de confianza para obtener más resultados
                    confidence = result.get('confidence', 0)
                    if confidence < 5:  # Umbral más permisivo
                        logger.warning(f"Baja confianza ({confidence}) para la ubicación: {location}")
                        return None
                    
                    lat = result['geometry']['lat']
                    lng = result['geometry']['lng']
                    
                    # Verificar que las coordenadas estén dentro del país correcto
                    bounds = country_bounds.get(country_code.lower())
                    if bounds:
                        if (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
                            bounds['min_lng'] <= lng <= bounds['max_lng']):
                            coordinates = (lat, lng)
                            self.cache[cache_key] = {
                                'coordinates': coordinates,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            self._save_cache()
                            return coordinates
                        else:
                            logger.warning(f"Coordenadas fuera del país para {location}: ({lat}, {lng})")
                            return None

            return None

        except Exception as e:
            logger.error(f"Error geocoding location {location}: {str(e)}")
            return None

    def _get_country_code(self, news_item: Dict) -> Optional[str]:
        """
        Obtener código de país desde la URL de la noticia o su contenido
        """
        # Mapeo de dominios específicos a países
        domain_country_map = {
            'infobae.com': 'ar',
            'clarin.com': 'ar',
            'lanacion.com.ar': 'ar',
            'pagina12.com.ar': 'ar',
            'emol.com': 'cl',
            'latercera.com': 'cl',
            'elmostrador.cl': 'cl',
            'elpais.com.uy': 'uy',
            'elobservador.com.uy': 'uy',
            'montevideo.com.uy': 'uy',
            'abc.com.py': 'py',
            'ultimahora.com': 'py',
            'lanacion.com.py': 'py',
            'eldeber.com.bo': 'bo',
            'paginasiete.bo': 'bo',
            'la-razon.com': 'bo'
        }

        try:
            domain = urlparse(news_item['link']).netloc.lower()
            # Eliminar 'www.' si existe
            domain = re.sub(r'^www\.', '', domain)
            
            # Buscar en el mapeo de dominios
            for known_domain, country in domain_country_map.items():
                if known_domain in domain:
                    return country
                    
            # Si no se encuentra en el mapeo, intentar extraer del TLD
            tld = domain.split('.')[-1].lower()
            if tld in ['ar', 'cl', 'uy', 'py', 'bo']:
                return tld
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting country from URL {news_item['link']}: {str(e)}")
            return None

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesa una noticia para obtener sus coordenadas y las guarda en la base de datos
        """
        try:
            # Extraer ubicaciones del título y contenido
            text = f"{news_item.get('title', '')} {news_item.get('content', '')}"
            locations = self.extract_locations(text)
            
            if not locations:
                return None
            
            for location in locations:
                # Verificar si ya existe en caché
                cached = self.cache.get(location)
                if cached:
                    coordinates = cached.get('coordinates')
                    if coordinates:
                        # Guardar en la base de datos
                        news_location = NewsLocation(
                            news_id=news_item['id'],
                            latitude=coordinates[0],
                            longitude=coordinates[1],
                            location_name=location,
                            country_code=self._get_country_code(news_item)
                        )
                        db.session.add(news_location)
                        continue

                # Si no está en caché, geocodificar
                coordinates = self.geocode_location(location)
                if coordinates:
                    # Guardar en caché
                    self.cache[location] = {
                        'coordinates': coordinates,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    self._save_cache()
                    
                    # Guardar en la base de datos
                    news_location = NewsLocation(
                        news_id=news_item['id'],
                        latitude=coordinates[0],
                        longitude=coordinates[1],
                        location_name=location,
                        country_code=self._get_country_code(news_item)
                    )
                    db.session.add(news_location)
            
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error processing news item: {str(e)}")
            db.session.rollback()
            return None
