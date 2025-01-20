from flask import current_app
import json
from datetime import datetime, timedelta
import os

class MarkerCacheService:
    def __init__(self):
        self.cache_file = 'markers_cache.json'
        self.cache_duration = timedelta(hours=24)

    def get_cached_markers(self):
        """Obtiene los marcadores del cache si son válidos"""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Verificar si el cache ha expirado
            last_update = datetime.fromisoformat(cache_data['last_update'])
            if datetime.now() - last_update > self.cache_duration:
                return None
                
            return cache_data['markers']
        except Exception as e:
            current_app.logger.error(f"Error leyendo cache de marcadores: {e}")
            return None

    def update_cache(self, markers):
        """Actualiza el cache con nuevos marcadores"""
        try:
            cache_data = {
                'last_update': datetime.now().isoformat(),
                'markers': markers
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            return True
        except Exception as e:
            current_app.logger.error(f"Error actualizando cache de marcadores: {e}")
            return False

    def needs_update(self):
        """Verifica si el cache necesita actualización"""
        cached_markers = self.get_cached_markers()
        return cached_markers is None
