#!/usr/bin/env python3
import os
from app import create_app, db
from app.models.news import News
from app.models.news_location import NewsLocation

def reset_database():
    """
    Limpia todas las noticias y ubicaciones de la base de datos
    """
    # Asegurarse de que el directorio instance existe
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    os.makedirs(instance_path, exist_ok=True)
    os.chmod(instance_path, 0o777)  # Dar permisos totales al directorio
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️ Eliminando todas las ubicaciones...")
            NewsLocation.query.delete()
            
            print("🗑️ Eliminando todas las noticias...")
            News.query.delete()
            
            db.session.commit()
            print("✅ Base de datos limpiada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error limpiando la base de datos: {str(e)}")
            db.session.rollback()
            return False
        
        return True

if __name__ == "__main__":
    reset_database()
