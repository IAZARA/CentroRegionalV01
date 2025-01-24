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
            if not text.strip():
                logger.warning("Texto vacío proporcionado a extract_locations")
                return []

            # Prompt para extraer ubicaciones
            prompt = f"""
            Analiza el siguiente texto y extrae todas las ubicaciones geográficas mencionadas que estén en Argentina.
            Es MUY IMPORTANTE que devuelvas SOLO un array JSON válido con la siguiente estructura, sin texto adicional:
            [
                {{
                    "name": "nombre de la ubicación",
                    "type": "city/province/neighborhood",
                    "is_primary": true/false
                }}
            ]
            
            Si no hay ubicaciones, devuelve [].
            
            Texto a analizar:
            {text}
            """
            
            logger.info(f"Analizando texto: {text[:200]}...")
            
            # Llamar a Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                system="Eres un asistente especializado en extraer ubicaciones geográficas de Argentina. SOLO debes responder con un array JSON válido.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if not response.content:
                logger.warning("Claude devolvió una respuesta vacía")
                return []

            # Procesar la respuesta
            response_text = response.content[0].text.strip()
            logger.info(f"Respuesta de Claude: {response_text}")

            try:
                # Intentar parsear directamente primero
                locations = json.loads(response_text)
                if isinstance(locations, list):
                    logger.info(f"Ubicaciones encontradas: {locations}")
                    return locations
                else:
                    logger.warning(f"La respuesta no es una lista: {response_text}")
                    return []
            except json.JSONDecodeError:
                # Si falla, intentar extraer el JSON
                import re
                json_match = re.search(r'\[(.*?)\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        locations = json.loads(f"[{json_match.group(1)}]")
                        logger.info(f"Ubicaciones encontradas (después de extracción): {locations}")
                        return locations
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al parsear JSON extraído: {str(e)}")
                        return []
                else:
                    logger.error("No se pudo encontrar un array JSON en la respuesta")
                    return []
                    
        except Exception as e:
            logger.error(f"Error en extract_locations: {str(e)}", exc_info=True)
            return []
