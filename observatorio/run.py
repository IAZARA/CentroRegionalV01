import os
import sys
import argparse
from app import create_app, db
from app.models.user import User, UserRoles

app = create_app()

with app.app_context():
    db.create_all()
    
    # Crear un usuario administrador si no existe
    admin = User.query.filter_by(email='ivan.zarate@minseg.gob.ar').first()
    if not admin:
        admin = User(
            email='ivan.zarate@minseg.gob.ar',
            nombre='Ivan',
            apellido='Zarate',
            telefono='0000000000',
            dependencia='Ministerio de Seguridad',
            role=UserRoles.ADMIN
        )
        admin.set_password('Minseg2025-')
        db.session.add(admin)
        db.session.commit()
        print(f"Usuario administrador creado: {admin.email}")

if __name__ == '__main__':
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Ejecutar el Observatorio de Drogas Sintéticas')
    parser.add_argument('--port', type=int, default=5001, help='Puerto en el que se ejecutará la aplicación')
    args = parser.parse_args()
    
    # Ejecutar la aplicación en el puerto especificado
    app.run(debug=True, host='0.0.0.0', port=args.port)
