import re
import logging
from typing import Dict, List, Optional, Tuple, Union
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
        self.cache = {}
        self.cache_file = 'geocoding_cache.json'
        self._load_cache()
        
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
        
        # Palabras a ignorar
        ignore_words = {
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
            'millones', 'miles', 'cientos', 'docenas'
        }
        
        locations = set()
        
        # Buscar ubicaciones usando los indicadores
        for pattern in location_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                # Verificar que la ubicación no sea una palabra a ignorar
                if not any(word in location.lower() for word in ignore_words):
                    locations.add(location)
        
        # Buscar ubicaciones conocidas directamente en el texto
        for location in known_locations:
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
                not any(word in loc.lower() for word in ignore_words) and  # No contiene palabras a ignorar
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

    def geocode_location(self, location: str) -> Optional[dict]:
        """
        Geocodificar una ubicación usando OpenCage
        """
        try:
            # Obtener el código de país
            country_code = self._get_country_code(location)
            
            # Construir el query con el país
            country_name = {
                'ar': 'Argentina',
                'cl': 'Chile',
                'mx': 'México',
                'co': 'Colombia',
                'pe': 'Perú',
                'bo': 'Bolivia',
                'ec': 'Ecuador',
                'py': 'Paraguay',
                'uy': 'Uruguay',
                'br': 'Brasil',
                've': 'Venezuela'
            }.get(country_code, 'Argentina')
            
            query = f"{location}, {country_name}"
            
            # Verificar caché
            if query in self.cache:
                logger.info(f"Ubicación encontrada en caché: {location}")
                return self.cache[query]
            
            logger.info(f"Búsqueda en OpenCage: {query}")
            logger.info(f"OpenCage API Key: {self.opencage_api_key[:5]}...")
            
            # Realizar la búsqueda
            response = requests.get(
                'https://api.opencagedata.com/geocode/v1/json',
                params={
                    'q': query,
                    'key': self.opencage_api_key,
                    'language': 'es',
                    'limit': 1,
                    'countrycode': country_code
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    result = data['results'][0]
                    
                    # Verificar la confianza del resultado
                    if result['confidence'] < 7:
                        logger.warning(f"Baja confianza ({result['confidence']}) para la ubicación: {location}")
                    
                    # Obtener las coordenadas
                    coords = result['geometry']
                    logger.info(f"Coordenadas encontradas para {location}: ({coords['lat']}, {coords['lng']})")
                    
                    # Guardar en caché
                    geocoded = {
                        'latitude': coords['lat'],
                        'longitude': coords['lng'],
                        'country_code': country_code
                    }
                    self.cache[query] = geocoded
                    return geocoded
            
            return None
            
        except Exception as e:
            logger.error(f"Error geocodificando {location}: {str(e)}")
            return None

    def process_news_item(self, news_item: Dict) -> Optional[Dict]:
        """
        Procesa una noticia para obtener sus coordenadas y las guarda en la base de datos
        """
        try:
            # Extraer texto relevante de la noticia
            text = f"{news_item.get('title', '')} {news_item.get('description', '')}"
            logger.info(f"Extrayendo ubicaciones del texto: {text[:100]}...")
            
            # Extraer ubicaciones del texto
            locations = self.extract_locations(text)
            logger.info(f"Ubicaciones encontradas: {locations}")
            
            if not locations:
                return None
                
            # Determinar la fuente y categoría
            source = self._get_source(news_item)
            category = self._determine_category(news_item)
            
            # Geocodificar cada ubicación
            processed_locations = []
            for location in locations:
                geocoded = self.geocode_location(location)
                if geocoded:
                    processed_location = {
                        'name': location,
                        'latitude': float(geocoded['latitude']) if isinstance(geocoded['latitude'], str) else geocoded['latitude'],
                        'longitude': float(geocoded['longitude']) if isinstance(geocoded['longitude'], str) else geocoded['longitude'],
                        'country_code': geocoded['country_code'],
                        'source': source,
                        'category': category
                    }
                    processed_locations.append(processed_location)
            
            if not processed_locations:
                return None
                
            return {
                'news_id': news_item['id'],
                'locations': processed_locations,
                'source': source,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error procesando ubicaciones para noticia {news_item.get('id')}: {str(e)}")
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

    def save_location(self, news_id: int, location_name: str, latitude: float, longitude: float) -> None:
        """
        Guardar una ubicación en la base de datos
        """
        try:
            logger.info(f"Guardando ubicación: {location_name} ({latitude}, {longitude}) para noticia {news_id}")
            # Verificar si ya existe una ubicación similar para esta noticia
            existing_location = NewsLocation.query.filter_by(
                news_id=news_id,
                location_name=location_name
            ).first()
            
            if not existing_location:
                location = NewsLocation(
                    news_id=news_id,
                    location_name=location_name,
                    latitude=latitude,
                    longitude=longitude
                )
                db.session.add(location)
                db.session.commit()
                logger.info(f"Ubicación guardada: {location_name} ({latitude}, {longitude})")
            else:
                logger.info(f"Ubicación ya existe: {location_name}")
            
        except Exception as e:
            logger.error(f"Error saving location {location_name}: {str(e)}")
            db.session.rollback()
