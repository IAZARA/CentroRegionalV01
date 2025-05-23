from flask import Flask, session, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from celery import Celery
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
celery = Celery(__name__, broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

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
    # Crear la aplicación Flask con el directorio instance explícito
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates',
                instance_path=instance_path)
    
    # Asegurarse de que el directorio instance existe
    os.makedirs(instance_path, exist_ok=True)
    
    # Cargar variables de entorno desde .env
    env_path = os.path.join(os.path.dirname(instance_path), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        app.logger.info("Variables de entorno cargadas desde .env")
        app.logger.info(f"MAPBOX_TOKEN: {os.environ.get('MAPBOX_TOKEN', 'No encontrado')}")
    
    app.config.from_object(config_class)
    
    # Configurar logging
    file_handler = RotatingFileHandler('instance/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Observatorio startup')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        if 'language' in session:
            return session['language']
        return current_app.config['BABEL_DEFAULT_LOCALE']
    
    # Configurar login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User, GuestUser
        if user_id == '-1':
            return GuestUser()
        try:
            return User.query.get(int(user_id))
        except:
            return None

    # Importar modelos
    from app.models import News, NewsLocation, User
    
    celery.conf.update(app.config)

    # Crear las tablas de la base de datos
    with app.app_context():
        db.create_all()
        create_admin_user()  # Crear usuario admin si no existe

    # Registrar blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
