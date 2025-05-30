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
- PostgreSQL 12+
- Mapbox API Key
- Dependencias de Python listadas en requirements.txt

## Configuración

1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno en `.env`:
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

## Uso

Para ejecutar el servidor de desarrollo:
```bash
flask run
```

El servidor estará disponible en `http://localhost:5000`

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