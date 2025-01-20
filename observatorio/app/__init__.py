from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde .env

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

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class is None:
        # Configuración desde variables de entorno
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///observatorio.db')
        app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY')
        app.config['GOOGLE_SEARCH_ENGINE_ID'] = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        app.config['MAPBOX_TOKEN'] = os.environ.get('MAPBOX_TOKEN')
        app.config['OPENCAGE_API_KEY'] = os.environ.get('OPENCAGE_API_KEY')
        
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
