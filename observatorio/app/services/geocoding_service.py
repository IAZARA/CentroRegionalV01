import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
import requests
from flask import current_app
from datetime import datetime
import json
import os
from app import db
from app.models.news_location import NewsLocation

logger = logging.getLogger(__name__)

class GeocodingService:
    def __init__(self):
        self.opencage_api_key = current_app.config['OPENCAGE_API_KEY']
        self.cache = {}
        self.cache_file = 'geocoding_cache.json'
        self._load_cache()
        
        # Palabras a ignorar en la detección de ubicaciones
        self.ignore_words = {
            # Títulos y nombres
            'señor', 'don', 'doña', 'sr', 'sra', 'dr', 'dra', 'lic', 'ing',
            
            # Pronombres y artículos
            'su', 'este', 'esta', 'aquel', 'aquella', 'el', 'la', 'los', 'las',
            
            # Términos genéricos
            'jurisdicción', 'sector', 'zona', 'área', 'región', 'lugar', 'sitio',
            'punto', 'parte', 'lado', 'centro', 'norte', 'sur', 'este', 'oeste',
            
            # Términos relacionados con drogas y crimen
            'droga', 'drogas', 'cocaína', 'marihuana', 'narcotráfico', 'operativo',
            'decomiso', 'incautación', 'laboratorio', 'laboratorios', 'cárcel',
            'prisión', 'penal', 'comisaría', 'policía', 'investigación',
            
            # Términos administrativos
            'gobierno', 'ministerio', 'secretaría', 'departamento', 'oficina',
            'dependencia', 'institución', 'organismo', 'entidad',
            
            # Otros términos comunes
            'acceso', 'manera', 'forma', 'modo', 'tipo', 'clase', 'especie',
            'cantidad', 'número', 'total', 'pesos', 'dólares', 'euros',
            'millones', 'miles', 'cientos', 'docenas',
            
            # Nuevos términos a ignorar
            'airbnb', 'será', 'castigada', 'hasta', 'parecía', 'idea',
            'emergiendo', 'prohibición', 'supuesta'
        }

        # Ubicaciones conocidas con sus países
        self.known_locations = {
            'Mexicali': 'México',
            'Culiacán': 'México',
            'Sinaloa': 'México',
            'Guerrero': 'México',
            'Antioquia': 'Colombia',
            'Rosario': 'Argentina',
            'Mendoza': 'Argentina',
            'Salta': 'Argentina',
            'Chile': 'Chile',
            'Son Banya': 'España'
        }
        
        # Actualizar el mapeo de dominios a países
        self.country_domains = {
            # Argentina
            'infobae.com': 'ar',
            'clarin.com': 'ar',
            'lanacion.com.ar': 'ar',
            'pagina12.com.ar': 'ar',
            'perfil.com': 'ar',
            'ambito.com': 'ar',
            'telam.com.ar': 'ar',
            'cronista.com': 'ar',
            
            # Chile
            'emol.com': 'cl',
            'latercera.com': 'cl',
            'cooperativa.cl': 'cl',
            'biobiochile.cl': 'cl',
            't13.cl': 'cl',
            '24horas.cl': 'cl',
            'elmostrador.cl': 'cl',
            
            # México
            'eluniversal.com.mx': 'mx',
            'excelsior.com.mx': 'mx',
            'milenio.com': 'mx',
            'jornada.com.mx': 'mx',
            'reforma.com': 'mx',
            'proceso.com.mx': 'mx',
            
            # Colombia
            'eltiempo.com': 'co',
            'elespectador.com': 'co',
            'semana.com': 'co',
            'caracol.com.co': 'co',
            'rcnradio.com': 'co',
            'bluradio.com': 'co',
            
            # Perú
            'elcomercio.pe': 'pe',
            'larepublica.pe': 'pe',
            'peru21.pe': 'pe',
            'rpp.pe': 'pe',
            'gestion.pe': 'pe',
            
            # Uruguay
            'elpais.com.uy': 'uy',
            'elobservador.com.uy': 'uy',
            'montevideo.com.uy': 'uy',
            'republica.com.uy': 'uy',
            
            # Paraguay
            'abc.com.py': 'py',
            'ultimahora.com': 'py',
            'lanacion.com.py': 'py',
            
            # Bolivia
            'eldeber.com.bo': 'bo',
            'paginasiete.bo': 'bo',
            'lostiempos.com': 'bo',
            'la-razon.com': 'bo',
            
            # Ecuador
            'elcomercio.com': 'ec',
            'eluniverso.com': 'ec',
            'expreso.ec': 'ec',
            
            # Venezuela
            'elnacional.com': 've',
            'eluniversal.com': 've',
            'ultimasnoticias.com.ve': 've'
        }

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
        logger.info(f"Extrayendo ubicaciones del texto: {text[:100]}...")
        
        # Lista de palabras que indican que lo que sigue es una ubicación
        location_indicators = [
            r'(?:en|desde|hasta|hacia)\s+(?:la\s+)?(?:ciudad\s+de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            r'(?:provincia|estado|región|departamento)\s+(?:de|del)?\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            r'(?:municipio|localidad|barrio)\s+(?:de|del)?\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)'
        ]
        
        # Lista de ubicaciones conocidas con sus códigos de país
        known_locations = {
            # Argentina
            'Buenos Aires': 'ar', 'Córdoba': 'ar', 'Rosario': 'ar', 'Mendoza': 'ar', 'La Plata': 'ar',
            'Mar del Plata': 'ar', 'San Miguel de Tucumán': 'ar', 'Salta': 'ar', 'Santa Fe': 'ar',
            'San Juan': 'ar', 'Resistencia': 'ar', 'Neuquén': 'ar', 'Formosa': 'ar', 'San Luis': 'ar',
            'La Rioja': 'ar', 'Catamarca': 'ar', 'Corrientes': 'ar', 'Río Cuarto': 'ar',
            'Bariloche': 'ar', 'Tandil': 'ar', 'Jujuy': 'ar',
            
            # Chile
            'Santiago': 'cl', 'Valparaíso': 'cl', 'Concepción': 'cl', 'Antofagasta': 'cl',
            'Viña del Mar': 'cl', 'Talca': 'cl', 'Rancagua': 'cl', 'Temuco': 'cl',
            'Iquique': 'cl', 'Puerto Montt': 'cl', 'Arica': 'cl', 'Calama': 'cl',
            'La Serena': 'cl', 'Copiapó': 'cl', 'Coquimbo': 'cl', 'Osorno': 'cl',
            'Valdivia': 'cl', 'Punta Arenas': 'cl', 'Chillán': 'cl', 'Los Ángeles': 'cl',
            'La Calera': 'cl', 'San Antonio': 'cl',
            
            # Uruguay
            'Montevideo': 'uy', 'Punta del Este': 'uy', 'Maldonado': 'uy', 'Salto': 'uy',
            'Paysandú': 'uy', 'Rivera': 'uy', 'Las Piedras': 'uy', 'Melo': 'uy',
            
            # Paraguay
            'Asunción': 'py', 'Ciudad del Este': 'py', 'Encarnación': 'py', 'Luque': 'py',
            'San Lorenzo': 'py', 'Lambaré': 'py', 'Fernando de la Mora': 'py',
            
            # Bolivia
            'La Paz': 'bo', 'Santa Cruz': 'bo', 'Cochabamba': 'bo', 'Sucre': 'bo',
            'Oruro': 'bo', 'Potosí': 'bo', 'Tarija': 'bo', 'Trinidad': 'bo',
            
            # México
            'Guerrero': 'mx',
            'Estado de Guerrero': 'mx',
            'Culiacán': 'mx',
            'Culiacan': 'mx',
            'Sinaloa': 'mx',
            'Estado de Sinaloa': 'mx',
            'Mexicali': 'mx',
            'Baja California': 'mx',
            'Estado de Baja California': 'mx',
            'Ciudad de México': 'mx',
            'Ciudad de Mexico': 'mx',
            'CDMX': 'mx',
            'Tijuana': 'mx',
            'Guadalajara': 'mx',
            'Monterrey': 'mx',
            'Cancún': 'mx',
            'Cancun': 'mx',
            'Chihuahua': 'mx',
            'Estado de Chihuahua': 'mx',
            'Sonora': 'mx',
            'Estado de Sonora': 'mx',
            'Tamaulipas': 'mx',
            'Estado de Tamaulipas': 'mx',
            'Nuevo León': 'mx',
            'Nuevo Leon': 'mx',
            'Estado de Nuevo León': 'mx',
            'Estado de Nuevo Leon': 'mx',
            'Jalisco': 'mx',
            'Estado de Jalisco': 'mx',
            'Michoacán': 'mx',
            'Michoacan': 'mx',
            'Estado de Michoacán': 'mx',
            'Estado de Michoacan': 'mx'
        }
        
        locations = set()
        
        # Buscar ubicaciones usando los indicadores
        for pattern in location_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                # Verificar que la ubicación no sea una palabra a ignorar
                if not any(word in location.lower() for word in self.ignore_words):
                    locations.add(location)
        
        # Buscar ubicaciones conocidas directamente en el texto
        for location in self.known_locations:
            if re.search(r'\b' + re.escape(location) + r'\b', text):
                locations.add(location)
        
        # Normalizar y filtrar ubicaciones
        normalized_locations = set()
        for loc in locations:
            # Remover artículos y preposiciones al inicio
            loc = re.sub(r'^(?:el|la|los|las|de|del|en)\s+', '', loc, flags=re.IGNORECASE)
            # Remover palabras comunes al inicio
            loc = re.sub(r'^(?:ciudad|provincia|estado|región|departamento|municipio|localidad|barrio)\s+(?:de|del)?\s+', '', loc, flags=re.IGNORECASE)
            # Si después de la normalización la ubicación es válida, agregarla
            if (len(loc) > 2 and  # Más de 2 caracteres
                not any(word in loc.lower() for word in self.ignore_words) and  # No contiene palabras a ignorar
                not re.match(r'\d', loc) and  # No empieza con número
                not loc.isupper() and  # No es todo mayúsculas
                re.match(r'^[A-ZÁÉÍÓÚÑ]', loc)):  # Comienza con mayúscula
                normalized_locations.add(loc)
        
        logger.info(f"Ubicaciones encontradas: {list(normalized_locations)}")
        return list(normalized_locations)

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

    def _get_country_code(self, location_or_news: Union[str, Dict]) -> Optional[str]:
        """
        Determinar el código de país más probable para una ubicación o noticia
        """
        # Si es una noticia, intentar obtener el país del dominio
        if isinstance(location_or_news, dict):
            try:
                url = location_or_news.get('link', '')
                if not url:
                    return None
                    
                domain = urlparse(url).netloc.lower()
                # Eliminar 'www.' si existe
                domain = re.sub(r'^www\.', '', domain)
                
                # Buscar en el mapeo de dominios
                for known_domain, country in self.country_domains.items():
                    if known_domain in domain:
                        logger.info(f"País encontrado por dominio {domain}: {country}")
                        return country
                        
                # Si no se encuentra en el mapeo, intentar extraer del TLD
                tld = domain.split('.')[-1].lower()
                if tld in ['ar', 'cl', 'uy', 'py', 'bo', 'mx', 'co', 'pe', 'ec', 've']:
                    logger.info(f"País encontrado por TLD {tld}")
                    return tld
                    
                # Buscar menciones de países en el título y descripción
                text = f"{location_or_news.get('title', '')} {location_or_news.get('description', '')}".lower()
                country_mentions = {
                    'argentina': 'ar', 'chile': 'cl', 'méxico': 'mx', 'mexico': 'mx',
                    'colombia': 'co', 'perú': 'pe', 'peru': 'pe', 'uruguay': 'uy',
                    'paraguay': 'py', 'bolivia': 'bo', 'ecuador': 'ec', 'venezuela': 've'
                }
                
                for country_name, code in country_mentions.items():
                    if country_name in text:
                        logger.info(f"País encontrado en el texto: {code}")
                        return code
                        
            except Exception as e:
                logger.error(f"Error obteniendo país del dominio: {str(e)}")
                return None
        
        # Si es una ubicación o si no se pudo obtener el país del dominio,
        # usar el mapeo de ubicaciones conocidas
        if isinstance(location_or_news, str):
            location = location_or_news.lower()
        else:
            location = ""
            
        # Mapeo de ubicaciones conocidas a países
        location_country_map = {
            # Argentina
            'buenos aires': 'ar', 'córdoba': 'ar', 'rosario': 'ar', 'mendoza': 'ar',
            'la plata': 'ar', 'mar del plata': 'ar', 'tucumán': 'ar', 'salta': 'ar',
            
            # Chile
            'santiago': 'cl', 'valparaíso': 'cl', 'concepción': 'cl', 'antofagasta': 'cl',
            'viña del mar': 'cl', 'talcahuano': 'cl', 'iquique': 'cl', 'temuco': 'cl',
            'chile': 'cl',
            
            # México
            'ciudad de méxico': 'mx', 'guadalajara': 'mx', 'monterrey': 'mx', 'puebla': 'mx',
            'tijuana': 'mx', 'león': 'mx', 'juárez': 'mx', 'méxico': 'mx', 'sinaloa': 'mx',
            'guerrero': 'mx', 'jalisco': 'mx',
            
            # Colombia
            'bogotá': 'co', 'medellín': 'co', 'cali': 'co', 'barranquilla': 'co',
            'cartagena': 'co', 'cúcuta': 'co', 'bucaramanga': 'co', 'antioquia': 'co',
            'valle del cauca': 'co', 'colombia': 'co',
            
            # Otros países
            'montevideo': 'uy', 'asunción': 'py', 'la paz': 'bo', 'santa cruz': 'bo',
            'lima': 'pe', 'quito': 'ec', 'guayaquil': 'ec', 'caracas': 've'
        }
        
        # Buscar coincidencias en el mapeo
        for key, country in location_country_map.items():
            if key in location.lower():
                logger.info(f"País encontrado para {location}: {country}")
                return country
        
        # Si no se encuentra coincidencia, retornar None
        logger.warning(f"No se pudo determinar el país para la ubicación: {location}")
        return None

    def geocode_location(self, location: str) -> Optional[Dict]:
        """
        Geocodificar una ubicación usando OpenCage o caché
        """
        try:
            # Obtener el código de país si está disponible
            country_code = self.get_country_code(location)
            if country_code:
                country_name = {
                    'ar': 'Argentina',
                    'cl': 'Chile',
                    'co': 'Colombia',
                    'mx': 'México',
                    'pe': 'Perú',
                    'py': 'Paraguay',
                    'uy': 'Uruguay',
                    'es': 'España'
                }.get(country_code)
                if country_name:
                    search_query = f"{location}, {country_name}"
                    
            logger.info(f"Búsqueda en OpenCage: {search_query}")
            logger.info(f"OpenCage API Key: {self.opencage_api_key[:5]}...")
            
            cached_location = self.cache.get(location)
            if cached_location:
                logger.info(f"Ubicación encontrada en caché: {location} ({cached_location['lat']}, {cached_location['lng']})")
                return {
                    'geometry': {
                        'lat': cached_location['lat'],
                        'lng': cached_location['lng']
                    },
                    'components': {
                        'country_code': cached_location.get('country_code', '')
                    }
                }
            
            # Si no está en caché, usar OpenCage
            params = {
                'q': location,
                'key': self.opencage_api_key,
                'limit': 1,
                'language': 'es'
            }
            
            response = requests.get("https://api.opencagedata.com/geocode/v1/json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['results']:
                result = data['results'][0]
                
                # Guardar en caché
                self.cache[location] = {
                    'lat': result['geometry']['lat'],
                    'lng': result['geometry']['lng'],
                    'country_code': result['components'].get('country_code', '').lower()
                }
                
                return {
                    'geometry': result['geometry'],
                    'components': {
                        'country_code': result['components'].get('country_code', '').lower()
                    }
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error geocodificando {location}: {str(e)}")
            return None

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesar una noticia para extraer y geocodificar sus ubicaciones
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
                        lat = geocoded_data['geometry'].get('lat')
                        lng = geocoded_data['geometry'].get('lng')
                        
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
                                    'country_code': geocoded_data.get('components', {}).get('country_code', '').lower()
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

    def save_location(self, location_data: Dict, news_item: Dict) -> Optional[Dict]:
        """
        Guardar una ubicación en la base de datos
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
                location_name=news_item.get('location', ''),
                latitude=lat,
                longitude=lng
            ).first()
            
            if not location:
                location = NewsLocation(
                    news_id=news_item['id'],
                    location_name=news_item.get('location', ''),
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
