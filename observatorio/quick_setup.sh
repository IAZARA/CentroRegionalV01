#!/bin/bash

# Script de configuración rápida para desarrollo
# Observatorio de Drogas Sintéticas

echo "=== Configuración Rápida - Observatorio ==="
echo

# Verificar si estamos en el directorio correcto
if [ ! -f "run.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio del proyecto (donde está run.py)"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorio instance si no existe
mkdir -p instance

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️  Creando archivo de configuración .env..."
    cat > .env << 'EOF'
SECRET_KEY=dev-secret-key-12345
FLASK_ENV=development
REDIS_URL=redis://localhost:6379/0
APIFY_API_TOKEN=tu_token_apify_aqui
EOF
fi

# Ejecutar script de creación de usuario admin
echo "👤 Configurando usuario administrador..."
python3 setup_admin.py

echo
echo "✅ Configuración completada!"
echo
echo "Para iniciar la aplicación:"
echo "  source venv/bin/activate"
echo "  python3 run.py"
echo
echo "Usuario administrador:"
echo "  📧 Email: ivan.zarate@minseg.gob.ar"
echo "  🔑 Contraseña: Minseg2025-"
echo
echo "La aplicación estará disponible en: http://localhost:5001"