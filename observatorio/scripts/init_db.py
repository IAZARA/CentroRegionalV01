#!/usr/bin/env python3
import os
from app import create_app, db
from app.models.user import User, UserRoles

def init_db():
    """
    Inicializa la base de datos y crea el usuario administrador.
    También asegura que el directorio instance exista.
    """
    # Crear el directorio instance si no existe
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    os.makedirs(instance_path, exist_ok=True)
    
    # Ruta de la base de datos
    db_path = os.path.join(instance_path, 'observatorio.db')
    print(f"Inicializando base de datos en: {db_path}")
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Crear usuario administrador si no existe
            admin = User.query.filter_by(email='admin@minseg.gob.ar').first()
            if not admin:
                admin = User(
                    email='admin@minseg.gob.ar',
                    nombre='Administrador',
                    apellido='Sistema',
                    telefono='0000000000',
                    dependencia='Ministerio de Seguridad',
                    role=UserRoles.ADMIN,
                    first_login=False
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print('✅ Usuario administrador creado exitosamente')
            else:
                print('ℹ️ El usuario administrador ya existe')
                
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")
            raise

if __name__ == '__main__':
    init_db()
