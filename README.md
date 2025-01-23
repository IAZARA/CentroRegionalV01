# Observatorio de Drogas Sintéticas

Sistema de monitoreo y análisis para el seguimiento de drogas sintéticas.

## Requisitos

- Python 3.8+
- Redis (para tareas en segundo plano)
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con:
```
DATABASE_URL=sqlite:///instance/observatorio.db
SECRET_KEY=dev-key-12345
REDIS_URL=redis://localhost:6379/0
MAPBOX_TOKEN=your_mapbox_token
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
OPENCAGE_API_KEY=your_opencage_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

## Estructura del Proyecto

```
observatorio/
├── app/                            # Directorio principal de la aplicación
│   ├── __init__.py                # Inicialización de la aplicación Flask
│   ├── models/                    # Modelos de la base de datos
│   │   ├── __init__.py
│   │   ├── user.py               # Modelo de usuarios y roles
│   │   ├── news.py               # Modelo de noticias
│   │   └── news_location.py      # Modelo de ubicaciones de noticias
│   ├── routes/                   # Rutas de la API
│   │   ├── __init__.py
│   │   ├── main/                 # Rutas principales
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # Endpoints principales
│   │   └── api.py               # Endpoints de la API
│   ├── main/                     # Blueprint principal
│   │   ├── __init__.py
│   │   └── routes.py            # Rutas del dashboard
│   ├── auth/                     # Sistema de autenticación
│   │   ├── __init__.py
│   │   └── routes.py            # Rutas de autenticación
│   ├── templates/               # Plantillas HTML
│   │   ├── auth/               # Templates de autenticación
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── change_password.html
│   │   ├── main/               # Templates principales
│   │   │   ├── home.html
│   │   │   ├── feed_new.html
│   │   │   ├── geomap.html
│   │   │   └── sidebar.html
│   │   ├── base.html           # Template base
│   │   └── base_dashboard.html # Template base del dashboard
│   ├── static/                 # Archivos estáticos
│   │   ├── css/
│   │   │   └── style.css      # Estilos personalizados
│   │   ├── js/
│   │   │   └── main.js        # JavaScript principal
│   │   └── img/               # Imágenes y logos
│   ├── services/              # Servicios de la aplicación
│   │   ├── __init__.py
│   │   ├── news_service.py    # Servicio de noticias
│   │   └── geocoding_service.py # Servicio de geocodificación
│   ├── forms/                 # Formularios
│   │   ├── __init__.py
│   │   └── auth.py           # Formularios de autenticación
│   └── utils/                # Utilidades
│       └── __init__.py
├── migrations/               # Migraciones de la base de datos
│   ├── versions/            # Versiones de las migraciones
│   ├── env.py              # Configuración del entorno
│   └── script.py.mako      # Template de migraciones
├── instance/               # Datos de la instancia
│   ├── observatorio.db    # Base de datos SQLite
│   └── app.log           # Logs de la aplicación
├── tests/                 # Pruebas unitarias
│   ├── __init__.py
│   ├── conftest.py       # Configuración de pruebas
│   └── test_*.py         # Archivos de prueba
├── scripts/              # Scripts de utilidad
│   └── backup.py        # Script de respaldo
├── cache/               # Caché de la aplicación
│   └── geocoding_cache.json
├── backups/            # Respaldos de la base de datos
├── .env               # Variables de entorno
├── .gitignore        # Archivos ignorados por git
├── requirements.txt  # Dependencias del proyecto
└── run.py           # Punto de entrada de la aplicación
```

## Configuración Actual

### Base de Datos
- SQLite para desarrollo local
- Migraciones automáticas con Flask-Migrate
- Usuario administrador predeterminado creado automáticamente

### Autenticación
- Sistema de login implementado con Flask-Login
- Credenciales del administrador:
  - Email: admin@minseg.gob.ar
  - Contraseña: Admin123!

### Rutas Principales
- `/auth/login` - Página de inicio de sesión
- `/home` - Dashboard principal
- `/geomap` - Visualización geográfica de datos
- `/noticias` - Feed de noticias

## Uso

1. Activar el entorno virtual:
```bash
source venv/bin/activate
```

2. Iniciar el servidor:
```bash
flask run
```

3. Acceder a la aplicación:
- URL: http://127.0.0.1:5000
- Iniciar sesión con las credenciales del administrador

## Módulos Implementados

### Sistema de Acceso y Seguridad
- Autenticación de usuarios
- Gestión de sesiones
- Protección de rutas

### Dashboard de Inteligencia
- Visualización de estadísticas
- Monitoreo de actividades
- Interfaz responsive

### Mapeo y Geolocalización
- Integración con Mapbox
- Visualización de datos geográficos
- Análisis espacial

### Sistema de Noticias
- Agregación de noticias
- Filtrado por países
- Estadísticas de publicaciones

## Próximas Mejoras
- Implementación de roles de usuario
- Sistema de notificaciones
- Mejoras en la visualización de datos
- Integración con más fuentes de datos

## Servicios Integrados
- Mapbox para visualización geográfica
- Google API para búsquedas
- OpenCage para geocodificación
- Anthropic para procesamiento de lenguaje natural
- Redis para tareas en segundo plano

## Licencia

[Tipo de Licencia]
