import os
import logging
import anthropic
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("No se encontró ANTHROPIC_API_KEY en las variables de ambiente")
            raise ValueError("ANTHROPIC_API_KEY no está configurada")
        logger.info("Inicializando AnthropicService...")
        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_locations(self, text: str) -> List[Dict]:
        """
        Extrae ubicaciones del texto usando Claude
        """
        try:
            # Instrucciones para Claude
            prompt = f"""Analiza el siguiente texto y extrae todas las ubicaciones geográficas mencionadas.
Para cada ubicación, proporciona:
1. El nombre específico de la ubicación
2. El estado/provincia/departamento (si se menciona)
3. El país (si se menciona)
4. El tipo de ubicación (city, state, country)
5. Si es la ubicación principal del texto (is_primary)

Responde en formato JSON como una lista de objetos con las propiedades: name, state, country, type, is_primary.
Si algún campo no está presente en el texto, omítelo del JSON.

Texto: {text}"""

            # Obtener respuesta de Claude
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0,
                system="Eres un asistente experto en extraer y analizar ubicaciones geográficas de textos en español.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extraer el JSON de la respuesta
            response_text = response.content[0].text
            # Encontrar el primer [ y último ] para extraer el JSON
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                locations = json.loads(json_str)
                logger.info(f"Ubicaciones extraídas: {locations}")
                return locations
            else:
                logger.warning("No se encontró JSON en la respuesta")
                return []

        except Exception as e:
            logger.error(f"Error extrayendo ubicaciones: {str(e)}")
            return []
