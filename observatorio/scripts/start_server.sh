#!/bin/bash

# Configurar variables de entorno
export DATABASE_URL="postgresql://postgres:Vortex733-@localhost:5432/observatorio"
export FLASK_APP=run
export FLASK_ENV=development

# Iniciar el servidor Flask en el puerto 5001
flask run -p 5001
