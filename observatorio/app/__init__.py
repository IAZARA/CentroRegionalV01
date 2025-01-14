from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from celery import Celery
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
celery = Celery(__name__)

def create_admin_user():
    from app.models.user import User, UserRoles
    
    # Verificar si ya existe un usuario administrador
    admin_user = User.query.filter_by(email='admin@minseg.gob.ar').first()
    if not admin_user:
        admin_user = User(
            nombre='Administrador',
            apellido='Sistema',
            email='admin@minseg.gob.ar',
            telefono='0000000000',
            dependencia='Ministerio de Seguridad',
            role=UserRoles.ADMIN,
            first_login=False  # El admin no necesita cambiar la contraseña
        )
        admin_user.set_password('Admin123!')
        db.session.add(admin_user)
        db.session.commit()
        print('Usuario administrador creado exitosamente.')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    celery.conf.update(app.config)

    # Registrar blueprints
    with app.app_context():
        from app.models import User
        db.create_all()
        create_admin_user()  # Crear usuario admin si no existe
        
        from app.routes import auth, main
        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)

    return app
