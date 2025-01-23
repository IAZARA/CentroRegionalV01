from anthropic import Anthropic
from typing import List, Dict, Optional
from flask import current_app
import json
import logging
import os

logger = logging.getLogger(__name__)

class ClaudeGeocodingService:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.cache = {}
        self.cache_file = 'claude_geocoding_cache.json'
        self._load_cache()

    def extract_locations(self, text: str) -> List[Dict]:
        """
        Extraer ubicaciones del texto usando Claude
        """
        if not text:
            return []

        # Verificar caché
        cache_key = hash(text)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            prompt = f"""Analiza el siguiente texto de noticia y extrae todas las ubicaciones geográficas mencionadas.
            Responde SOLO con un objeto JSON que contenga un array de ubicaciones. Cada ubicación debe tener:
            - name: nombre exacto de la ubicación
            - is_primary: true/false si es la ubicación principal
            - country: código de país (ar, cl, uy, py, bo, etc.)
            - context: breve descripción del contexto

            Ejemplo de respuesta esperada:
            {{"locations": [
                {{
                    "name": "Buenos Aires",
                    "is_primary": true,
                    "country": "ar",
                    "context": "lugar del operativo"
                }}
            ]}}

            Texto de la noticia:
            {text}"""

            message = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0,
                system="Eres un experto en análisis geográfico de noticias. Tu tarea es identificar ubicaciones geográficas en textos noticiosos, con especial énfasis en Argentina y países limítrofes. SOLO debes responder con JSON válido.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            try:
                # Limpiar la respuesta para asegurar que solo contiene JSON
                response_text = message.content[0].text.strip()
                if not response_text.startswith('{'):
                    response_text = response_text[response_text.find('{'):]
                if not response_text.endswith('}'):
                    response_text = response_text[:response_text.rfind('}')+1]
                
                response = json.loads(response_text)
                
                # Validar la estructura de la respuesta
                if 'locations' not in response:
                    return []
                
                # Guardar en caché
                self.cache[cache_key] = response['locations']
                self._save_cache()
                
                return response['locations']
            except json.JSONDecodeError as e:
                logger.error(f"Error decodificando JSON de Claude: {str(e)}")
                return []

        except Exception as e:
            logger.error(f"Error al extraer ubicaciones con Claude: {str(e)}")
            return []

    def _load_cache(self):
        """Cargar caché desde archivo"""
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    def _save_cache(self):
        """Guardar caché a archivo"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
