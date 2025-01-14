# Observatorio de Drogas Sintéticas

Sistema de monitoreo y análisis para el seguimiento de drogas sintéticas.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
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
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/observatorio_drogas
SECRET_KEY=tu_clave_secreta
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

## Estructura del Proyecto

```
observatorio/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Uso

Para ejecutar el servidor de desarrollo:
```bash
flask run
```

## Módulos Principales

- Sistema de Acceso y Seguridad
- Dashboard de Inteligencia
- Sistema de Monitoreo RRSS
- Gestión Documental
- Mapeo y Geolocalización

## Licencia

[Tipo de Licencia]
