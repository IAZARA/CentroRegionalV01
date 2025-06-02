#!/usr/bin/env python3
"""
Script para crear usuario administrador
Observatorio de Drogas Sintéticas
"""

import os
import sys
from app import create_app, db
from app.models.user import User, UserRoles

def create_admin_user():
    """Crear usuario administrador ivan.zarate@minseg.gob.ar"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        
        # Verificar si el usuario ya existe
        admin = User.query.filter_by(email='ivan.zarate@minseg.gob.ar').first()
        
        if admin:
            print(f"✓ El usuario administrador ya existe: {admin.email}")
            print(f"  Nombre: {admin.full_name}")
            print(f"  Rol: {admin.role}")
            return admin
        
        # Crear nuevo usuario administrador
        admin = User(
            email='ivan.zarate@minseg.gob.ar',
            nombre='Ivan',
            apellido='Zarate',
            telefono='0000000000',
            dependencia='Ministerio de Seguridad',
            role=UserRoles.ADMIN,
            is_active=True,
            first_login=False  # Ya configurado
        )
        
        admin.set_password('Minseg2025-')
        
        try:
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Usuario administrador creado exitosamente:")
            print(f"  Email: {admin.email}")
            print(f"  Nombre: {admin.full_name}")
            print(f"  Rol: {admin.role}")
            print(f"  Contraseña: Minseg2025-")
            return admin
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear usuario administrador: {e}")
            return None

def main():
    """Función principal"""
    print("=== Configuración de Usuario Administrador ===")
    print("Observatorio de Drogas Sintéticas")
    print()
    
    try:
        admin = create_admin_user()
        if admin:
            print()
            print("=== Configuración completada ===")
            print("Puedes iniciar sesión con las credenciales mostradas arriba.")
        else:
            print()
            print("=== Error en la configuración ===")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error general: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()