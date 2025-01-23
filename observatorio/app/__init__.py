from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from celery import Celery
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()  # Cargar variables de entorno desde .env

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
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

def create_app(config_class=None):
    # Crear la aplicación Flask con el directorio instance explícito
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates',
                instance_path=instance_path)
    
    # Asegurarse de que el directorio instance existe
    os.makedirs(instance_path, exist_ok=True)
    
    if config_class is None:
        # Configuración desde variables de entorno
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')
        
        # Configurar base de datos
        instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
        os.makedirs(instance_path, exist_ok=True)
        os.chmod(instance_path, 0o777)  # Dar permisos totales al directorio
        
        db_path = os.path.join(instance_path, 'observatorio.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Configurar login manager
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
        login_manager.login_message_category = 'info'
        
        # Configurar tokens de APIs
        app.config['MAPBOX_TOKEN'] = os.environ.get('MAPBOX_TOKEN')
        app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY')
        app.config['GOOGLE_SEARCH_ENGINE_ID'] = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        app.config['OPENCAGE_API_KEY'] = os.environ.get('OPENCAGE_API_KEY')
        app.config['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY')
        
        # Configuración de dominios por país
        app.config['COUNTRY_DOMAINS'] = {
            '.ar': {
                'name': 'Argentina',
                'domains': ['clarin.com', 'lanacion.com.ar', 'infobae.com', 'pagina12.com.ar', 'telam.com.ar']
            },
            '.cl': {
                'name': 'Chile',
                'domains': ['emol.com', 'latercera.com', 'cooperativa.cl', 'elmostrador.cl']
            },
            '.uy': {
                'name': 'Uruguay',
                'domains': ['elpais.com.uy', 'elobservador.com.uy', 'montevideo.com.uy']
            },
            '.py': {
                'name': 'Paraguay',
                'domains': ['abc.com.py', 'ultimahora.com', 'lanacion.com.py']
            },
            '.bo': {
                'name': 'Bolivia',
                'domains': ['eldeber.com.bo', 'la-razon.com', 'lostiempos.com']
            }
        }
    else:
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

    # Importar modelos
    from app.models import User, News

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
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
