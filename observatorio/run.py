import os
import sys
from app import create_app, db
from app.models.user import User, UserRoles

app = create_app()

with app.app_context():
    db.create_all()
    
    # Crear un usuario administrador si no existe
    admin = User.query.filter_by(email='admin@minseg.gob.ar').first()
    if not admin:
        admin = User(
            email='admin@minseg.gob.ar',
            nombre='Administrador',
            apellido='Sistema',
            telefono='0000000000',
            dependencia='Ministerio de Seguridad',
            role=UserRoles.ADMIN
        )
        admin.set_password('Minseg2025-')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5002)
