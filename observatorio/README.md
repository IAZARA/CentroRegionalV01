# Observatorio de Drogas Sintéticas

Sistema de monitoreo y análisis de noticias sobre drogas sintéticas en Argentina y países limítrofes.

## Características

- Recopilación automática de noticias de diferentes fuentes
- Geocodificación de ubicaciones mencionadas en las noticias
- Visualización en mapa interactivo con tema oscuro
- Análisis de tendencias y patrones
- Sistema de autenticación de usuarios
- API REST para acceso a datos

## Requisitos

- Python 3.8+
- SQLite (configuración por defecto) o PostgreSQL 12+ (opcional)
- Mapbox API Key (para funcionalidad de mapas)
- Dependencias de Python listadas en requirements.txt

## Configuración Inicial

1. **Clonar el repositorio**

2. **Crear y activar entorno virtual**:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configuración de la base de datos**:

   La aplicación está configurada para usar SQLite por defecto. Los datos se almacenarán en `instance/observatorio.db`.

   Si deseas usar PostgreSQL, modifica `config.py` con:
   ```python
   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
       'postgresql://postgres:tu_contraseña@localhost/observatorio'
   ```

5. **Inicializar la base de datos**:
```bash
flask db upgrade
```

## Iniciar la Aplicación

1. **Activar el entorno virtual** (si no está activo):
```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Iniciar el servidor de desarrollo**:
```bash
flask run --port 5001
```

3. **Acceder a la aplicación**:
   - URL: http://127.0.0.1:5001

## Credenciales de Acceso

- **Usuario administrador**: admin@minseg.gob.ar
- **Contraseña**: Admin123!

## Tareas Programadas

Para actualizar noticias manualmente:

- Últimas 24 horas: `python -m scripts.update_news`
- Últimos N días: `python -m scripts.update_news --days N`
- Últimas N horas: `python -m scripts.update_news --hours N`
- Reprocesar todas las ubicaciones: `python -m scripts.update_news --reprocess-all`

## Base de Datos

El sistema utiliza PostgreSQL como base de datos principal. La migración desde SQLite a PostgreSQL permite:
- Mayor escalabilidad
- Mejor manejo de concurrencia
- Búsquedas más eficientes
- Soporte para datos geoespaciales

## API

La API REST proporciona endpoints para:
- Consulta de noticias
- Ubicaciones geográficas
- Estadísticas y análisis

## Licencia

Este proyecto está bajo la Licencia MIT.


Para buscar noticias del último día (por defecto):

python -m scripts.update_news

Para buscar noticias de los últimos N días:

python -m scripts.update_news --days 3

Para buscar noticias de las últimas N horas:

python -m scripts.update_news --hours 12

Para reprocesar todas las ubicaciones (manteniendo las noticias):

python -m scripts.update_news --reprocess-all

source venv/bin/activate && flask run --port 5001