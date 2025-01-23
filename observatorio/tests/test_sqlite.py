import sqlite3
import os

# Obtener la ruta absoluta al directorio instance
instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))

# Asegurarse de que el directorio instance existe
os.makedirs(instance_path, exist_ok=True)

# Ruta completa a la base de datos
db_path = os.path.join(instance_path, 'test.db')

print(f"Intentando crear base de datos en: {db_path}")

try:
    # Intentar crear y conectar a la base de datos
    conn = sqlite3.connect(db_path)
    print("Conexión exitosa a SQLite")
    
    # Crear una tabla de prueba
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS test
                     (id INTEGER PRIMARY KEY, name TEXT)''')
    print("Tabla creada exitosamente")
    
    # Insertar algunos datos
    cursor.execute("INSERT INTO test (name) VALUES (?)", ("Test 1",))
    conn.commit()
    print("Datos insertados exitosamente")
    
    # Cerrar la conexión
    conn.close()
    print("Conexión cerrada exitosamente")
    
except sqlite3.Error as e:
    print(f"Error con SQLite: {e}")
except Exception as e:
    print(f"Error general: {e}")
