import re
import logging
from typing import List, Set

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
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
            
            # Términos temporales y conectores
            'mientras', 'tanto', 'luego', 'después', 'antes', 'durante',
            'cuando', 'donde', 'como', 'porque', 'aunque', 'sino',
            'entonces', 'además', 'también', 'asimismo', 'igualmente',
            
            # Verbos comunes
            'está', 'estaba', 'estuvo', 'estará', 'ser', 'estar', 'hacer',
            'tener', 'poder', 'decir', 'ver', 'dar', 'saber', 'querer',
            'pasar', 'deber', 'poner', 'parecer', 'quedar', 'creer',
            'llevar', 'dejar', 'seguir', 'encontrar', 'llamar', 'venir',
            'pensar', 'salir', 'volver', 'tomar', 'conocer', 'realizar',
            'vivir', 'sentir', 'tratar', 'mirar', 'contar', 'empezar',
            'esperar', 'buscar', 'existir', 'entrar', 'trabajar', 'escribir',
            'perder', 'recibir', 'ocurrir', 'vender', 'cambiar', 'nacer',
            'dirigir', 'morir', 'conseguir', 'comenzar', 'servir', 'sacar',
            'necesitar', 'mantener', 'resultar', 'leer', 'caer', 'cambiar',
            'terminar', 'permitir', 'aparecer', 'conseguir', 'comenzar',
            'servir', 'sacar', 'necesitar', 'mantener', 'resultar', 'leer',
            'caer', 'cambiar', 'terminar', 'permitir', 'aparecer'
        }

        # Patrones para detectar ubicaciones
        self.location_patterns = [
            # Patrones con indicadores explícitos de ubicación
            r'(?:en|desde|hasta|hacia|de)\s+(?:la\s+)?(?:ciudad|localidad|provincia|municipio|estado|región|departamento)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            
            # Patrones para direcciones y lugares específicos
            r'(?:calle|avenida|plaza|parque|barrio)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            
            # Patrones para referencias geográficas
            r'(?:norte|sur|este|oeste)\s+de\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            
            # Patrón para ubicaciones con contexto
            r'(?:ubicad[oa]|localizad[oa]|situad[oa])\s+(?:en|cerca\s+de)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
            
            # Patrón para nombres propios que coinciden con ubicaciones conocidas
            r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)\b'
        ]

        # Ubicaciones conocidas
        self.known_locations = {
            # Argentina
            'Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata',
            'Mar del Plata', 'San Miguel de Tucumán', 'Salta', 'Santa Fe',
            'San Juan', 'Resistencia', 'Neuquén', 'Formosa', 'San Luis',
            'La Rioja', 'Catamarca', 'Corrientes', 'Río Cuarto',
            'Bariloche', 'Tandil', 'Jujuy',
            
            # Chile
            'Santiago', 'Valparaíso', 'Concepción', 'Antofagasta',
            'Viña del Mar', 'Talca', 'Rancagua', 'Temuco',
            'Iquique', 'Puerto Montt', 'Arica', 'Calama',
            'La Serena', 'Copiapó', 'Coquimbo', 'Osorno',
            'Valdivia', 'Punta Arenas', 'Chillán', 'Los Ángeles',
            'La Calera', 'San Antonio',
            
            # Uruguay
            'Montevideo', 'Punta del Este', 'Maldonado', 'Salto',
            'Paysandú', 'Rivera', 'Las Piedras', 'Melo',
            
            # Paraguay
            'Asunción', 'Ciudad del Este', 'Encarnación', 'Luque',
            'San Lorenzo', 'Lambaré', 'Fernando de la Mora',
            
            # Bolivia
            'La Paz', 'Santa Cruz', 'Cochabamba', 'Sucre',
            'Oruro', 'Potosí', 'Tarija', 'Trinidad',
            
            # México
            'Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla',
            'Tijuana', 'León', 'Juárez', 'Culiacán', 'Sinaloa',
            'Guerrero', 'Jalisco', 'Mexicali', 'Baja California'
        }

    def extract_locations(self, text: str) -> List[str]:
        """
        Extrae ubicaciones de un texto usando patrones y una lista de ubicaciones conocidas
        """
        try:
            locations = set()
            
            # 1. Buscar ubicaciones usando patrones
            for pattern in self.location_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    location = match.group(1).strip()
                    if self._is_valid_location(location):
                        locations.add(location)
            
            # 2. Buscar ubicaciones conocidas
            for location in self.known_locations:
                if re.search(r'\b' + re.escape(location) + r'\b', text):
                    locations.add(location)
            
            # 3. Normalizar ubicaciones
            normalized = self._normalize_locations(locations)
            
            return list(normalized)
            
        except Exception as e:
            logger.error(f"Error extrayendo ubicaciones: {str(e)}")
            return []

    def _is_valid_location(self, location: str) -> bool:
        """
        Verifica si una ubicación es válida según ciertos criterios
        """
        # Convertir a minúsculas para las comparaciones
        location_lower = location.lower()
        
        # Verificaciones básicas
        if (len(location) <= 2 or  # Muy corto
            any(word.lower() in location_lower for word in self.ignore_words) or  # Contiene palabras a ignorar
            re.match(r'\d', location) or  # Empieza con número
            location.isupper() or  # Todo en mayúsculas
            not re.match(r'^[A-ZÁÉÍÓÚÑ]', location)):  # No empieza con mayúscula
            return False
            
        # Verificar si contiene solo letras y espacios (permitiendo tildes y ñ)
        if not re.match(r'^[A-ZÁÉÍÓÚÑa-záéíóúñ\s]+$', location):
            return False
            
        # Verificar que no sea una frase común
        words = location_lower.split()
        if len(words) > 4:  # Probablemente es una frase, no una ubicación
            return False
            
        # Verificar que no contenga verbos comunes en infinitivo
        common_verbs = {'ser', 'estar', 'hacer', 'tener', 'poder', 'decir', 'ver', 'dar'}
        if any(word.lower().endswith(('ar', 'er', 'ir')) for word in words):
            if any(word.lower()[:-2] in common_verbs for word in words):
                return False
                
        # Si está en la lista de ubicaciones conocidas, es válida
        if location in self.known_locations:
            return True
            
        # Si llegó hasta aquí, probablemente es una ubicación válida
        return True

    def _normalize_locations(self, locations: Set[str]) -> Set[str]:
        """
        Normaliza un conjunto de ubicaciones
        """
        normalized = set()
        for loc in locations:
            # Remover artículos y preposiciones al inicio
            loc = re.sub(r'^(?:el|la|los|las|de|del|en)\s+', '', loc, flags=re.IGNORECASE)
            
            # Remover palabras comunes al inicio
            loc = re.sub(r'^(?:ciudad|provincia|estado|región|departamento|municipio|localidad|barrio)\s+(?:de|del)?\s+', '', loc, flags=re.IGNORECASE)
            
            # Remover indicadores de dirección
            loc = re.sub(r'^(?:norte|sur|este|oeste)\s+(?:de)?\s+', '', loc, flags=re.IGNORECASE)
            
            # Remover palabras que indican ubicación
            loc = re.sub(r'^(?:ubicado|ubicada|localizado|localizada|situado|situada)\s+(?:en|cerca\s+de)?\s+', '', loc, flags=re.IGNORECASE)
            
            if self._is_valid_location(loc):
                # Si la ubicación está en la lista de conocidas, usar esa versión
                for known_loc in self.known_locations:
                    if loc.lower() == known_loc.lower():
                        loc = known_loc
                        break
                normalized.add(loc)
        
        return normalized
