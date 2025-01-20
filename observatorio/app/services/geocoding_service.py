import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from flask import current_app
from datetime import datetime
import json
import os

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
        # Normalizar texto
        text = text.lower()
        
        # Palabras a ignorar
        ignore_words = {
            'pesos', 'millones', 'drogas', 'metanfetamina', 'mdma', 'éxtasis', 
            'cocaína', 'marihuana', 'cannabis', 'narcotráfico', 'consumidores',
            'manera', 'sector', 'terminal', 'aduana', 'policía', 'gobierno',
            'estado', 'país', 'región'
        }
        
        # Patrones de ubicación específicos
        patterns = [
            # Ciudades y lugares específicos
            r'(?:en|desde|de|cerca de) (?:la ciudad de |el municipio de )?([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*)',
            # Referencias geográficas con preposiciones
            r'(?:en|desde|de|cerca de) (?:la |el |los |las )?([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*)'
        ]

        locations = []
        # Primero buscar en el texto original (sin lowercase) para mantener las mayúsculas
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.UNICODE)
            for match in matches:
                location = match.group(1).strip()
                # Validar la ubicación
                location_lower = location.lower()
                if (len(location) > 3 and  # Más de 3 caracteres
                    not any(word in location_lower for word in ignore_words) and  # No contiene palabras a ignorar
                    not re.match(r'\d', location) and  # No empieza con número
                    not re.match(r'[A-Z\s]+$', location)):  # No es todo mayúsculas
                    locations.append(location)

        return list(set(locations))  # Eliminar duplicados

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

    def geocode_location(self, location: str, country_code: str) -> Optional[Tuple[float, float]]:
        """
        Geocodificar una ubicación usando OpenCage Geocoding API
        """
        cache_key = f"{location}_{country_code}"
        
        # Verificar caché
        if cache_key in self.cache:
            return self.cache[cache_key]

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
            
            country_name = country_names.get(country_code.lower())
            if not country_name:
                return None

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
                    
                    # Verificar la confianza del resultado
                    confidence = result.get('confidence', 0)
                    if confidence < 7:  # Aumentar el umbral de confianza
                        print(f"Baja confianza ({confidence}) para la ubicación: {location}")
                        return None
                    
                    lat = result['geometry']['lat']
                    lng = result['geometry']['lng']
                    
                    # Verificar que las coordenadas estén dentro del país correcto
                    bounds = country_bounds.get(country_code.lower())
                    if bounds:
                        if (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
                            bounds['min_lng'] <= lng <= bounds['max_lng']):
                            coordinates = (lat, lng)
                            self.cache[cache_key] = coordinates
                            self._save_cache()
                            return coordinates
                        else:
                            print(f"Coordenadas fuera del país para {location}: ({lat}, {lng})")
                            return None

            return None

        except Exception as e:
            logger.error(f"Error geocoding location {location}: {str(e)}")
            return None

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesar un item de noticia para obtener sus coordenadas
        """
        try:
            print(f"\nProcesando noticia: {news_item.get('title')}")
            
            # Extraer ubicaciones del título y descripción
            locations = self.extract_locations(news_item['title'])
            if 'snippet' in news_item:
                locations.extend(self.extract_locations(news_item['snippet']))
            
            print(f"Ubicaciones encontradas: {locations}")

            # Obtener país de la URL
            country_code = news_item.get('country', '').replace('.', '')
            if not country_code:
                country_code = self.get_country_from_url(news_item['link'])
            
            print(f"Código de país: {country_code}")

            if not country_code:
                print("No se pudo determinar el país de la noticia")
                return None

            # Intentar geocodificar cada ubicación encontrada
            for location in locations:
                print(f"Intentando geocodificar: {location}")
                coordinates = self.geocode_location(location, country_code)
                if coordinates:
                    print(f"Coordenadas encontradas: {coordinates}")
                    return {
                        'id': hash(news_item['link']),
                        'coordinates': coordinates,
                        'news': news_item,
                        'location': location
                    }
                else:
                    print(f"No se encontraron coordenadas para: {location}")

            print("No se encontraron coordenadas para ninguna ubicación")
            return None

        except Exception as e:
            logger.error(f"Error processing news item: {str(e)}")
            print(f"Error al procesar la noticia: {str(e)}")
            return None
