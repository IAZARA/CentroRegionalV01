#!/bin/bash

# Script de despliegue para Digital Ocean Droplet
# Observatorio de Drogas Sintéticas

set -e  # Salir si cualquier comando falla

echo "=== Iniciando despliegue en Digital Ocean ==="

# Actualizar el sistema
echo "Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
echo "Instalando dependencias del sistema..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor redis-server postgresql postgresql-contrib git

# Crear usuario para la aplicación
echo "Creando usuario para la aplicación..."
sudo useradd -m -s /bin/bash observatorio || true

# Crear directorio de la aplicación
echo "Configurando directorio de la aplicación..."
sudo mkdir -p /var/www/observatorio
sudo chown observatorio:observatorio /var/www/observatorio

# Cambiar al usuario de la aplicación
echo "Configurando la aplicación..."
sudo -u observatorio bash << 'EOF'
cd /var/www/observatorio

# Clonar o copiar el código (asumiendo que ya está en el servidor)
# git clone <tu-repositorio> .

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Crear directorios necesarios
mkdir -p instance logs

EOF

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE observatorio;
CREATE USER observatorio_user WITH PASSWORD 'observatorio_password_2025';
GRANT ALL PRIVILEGES ON DATABASE observatorio TO observatorio_user;
\q
EOF

# Crear archivo de configuración de producción
echo "Creando archivo de configuración..."
sudo -u observatorio tee /var/www/observatorio/.env > /dev/null << 'EOF'
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2025
DATABASE_URL=postgresql://observatorio_user:observatorio_password_2025@localhost/observatorio
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=production
APIFY_API_TOKEN=tu_token_apify_aqui
EOF

# Crear script de inicialización con usuario admin
echo "Creando script de inicialización..."
sudo -u observatorio tee /var/www/observatorio/init_admin.py > /dev/null << 'EOF'
import os
import sys
sys.path.insert(0, '/var/www/observatorio')

from app import create_app, db
from app.models.user import User, UserRoles

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    
    # Crear usuario administrador específico
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
    else:
        print(f"Usuario administrador ya existe: {admin.email}")
EOF

# Actualizar config.py para producción
echo "Actualizando configuración para producción..."
sudo -u observatorio tee /var/www/observatorio/config_production.py > /dev/null << 'EOF'
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://observatorio_user:observatorio_password_2025@localhost/observatorio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    APIFY_API_TOKEN = os.environ.get('APIFY_API_TOKEN')
    
    COUNTRY_DOMAINS = {
        '.ar': {'name': 'Argentina', 'domains': ['clarin.com', 'lanacion.com.ar', 'infobae.com', 'pagina12.com.ar']},
        '.cl': {'name': 'Chile', 'domains': ['emol.com', 'latercera.com', 'elmostrador.cl']},
        '.uy': {'name': 'Uruguay', 'domains': ['elpais.com.uy', 'elobservador.com.uy', 'montevideo.com.uy']},
        '.py': {'name': 'Paraguay', 'domains': ['abc.com.py', 'ultimahora.com', 'lanacion.com.py']},
        '.bo': {'name': 'Bolivia', 'domains': ['eldeber.com.bo', 'paginasiete.bo', 'la-razon.com']},
    }
    
    LOGIN_DISABLED = False
    LOGIN_VIEW = 'auth.login'
    USE_SESSION_FOR_NEXT = True
    LANGUAGES = ['es', 'en', 'pt']
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
EOF

# Crear archivo WSGI
echo "Creando archivo WSGI..."
sudo -u observatorio tee /var/www/observatorio/wsgi.py > /dev/null << 'EOF'
import os
import sys

# Agregar el directorio de la aplicación al path
sys.path.insert(0, '/var/www/observatorio')

# Configurar la variable de entorno para usar la configuración de producción
os.environ['FLASK_ENV'] = 'production'

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
EOF

# Inicializar la base de datos y crear usuario admin
echo "Inicializando base de datos y creando usuario administrador..."
sudo -u observatorio bash << 'EOF'
cd /var/www/observatorio
source venv/bin/activate
export FLASK_ENV=production
python init_admin.py
EOF

# Configurar Gunicorn
echo "Configurando Gunicorn..."
sudo tee /etc/systemd/system/observatorio.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn instance to serve Observatorio
After=network.target

[Service]
User=observatorio
Group=www-data
WorkingDirectory=/var/www/observatorio
Environment="PATH=/var/www/observatorio/venv/bin"
ExecStart=/var/www/observatorio/venv/bin/gunicorn --workers 3 --bind unix:observatorio.sock -m 007 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configurar Celery
echo "Configurando Celery..."
sudo tee /etc/systemd/system/observatorio-celery.service > /dev/null << 'EOF'
[Unit]
Description=Celery Service para Observatorio
After=network.target

[Service]
Type=forking
User=observatorio
Group=observatorio
WorkingDirectory=/var/www/observatorio
Environment="PATH=/var/www/observatorio/venv/bin"
ExecStart=/var/www/observatorio/venv/bin/celery -A app.celery worker --loglevel=info --detach
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/observatorio > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/observatorio/observatorio.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/observatorio/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 16M;
}
EOF

# Habilitar el sitio de Nginx
sudo ln -sf /etc/nginx/sites-available/observatorio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configurar permisos
echo "Configurando permisos..."
sudo chown -R observatorio:www-data /var/www/observatorio
sudo chmod -R 755 /var/www/observatorio

# Habilitar y iniciar servicios
echo "Habilitando y iniciando servicios..."
sudo systemctl daemon-reload
sudo systemctl enable observatorio
sudo systemctl enable observatorio-celery
sudo systemctl enable redis-server
sudo systemctl enable postgresql
sudo systemctl enable nginx

sudo systemctl start redis-server
sudo systemctl start postgresql
sudo systemctl start observatorio
sudo systemctl start observatorio-celery
sudo systemctl restart nginx

# Configurar firewall
echo "Configurando firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "=== Despliegue completado ==="
echo "La aplicación debería estar disponible en http://$(curl -s ifconfig.me)"
echo "Usuario administrador creado:"
echo "  Email: ivan.zarate@minseg.gob.ar"
echo "  Contraseña: Minseg2025-"
echo ""
echo "Para verificar el estado de los servicios:"
echo "  sudo systemctl status observatorio"
echo "  sudo systemctl status observatorio-celery"
echo "  sudo systemctl status nginx"
echo ""
echo "Logs de la aplicación:"
echo "  sudo journalctl -u observatorio -f"
echo "  sudo journalctl -u observatorio-celery -f"