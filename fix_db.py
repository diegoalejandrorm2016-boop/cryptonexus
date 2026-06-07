import os
import shutil

def fix_database():
    db_file = 'crypto_platform.db'
    migrations_dir = os.path.join('trading', 'migrations')

    print("Iniciando reparación de la base de datos...")

    # 1. Eliminar la base de datos desincronizada
    if os.path.exists(db_file):
        os.remove(db_file)
        print("🗑️ Base de datos corrupta eliminada.")

    # 2. Resetear el caché de migraciones de la app trading
    if os.path.exists(migrations_dir):
        shutil.rmtree(migrations_dir)
        print("🗑️ Caché de migraciones antigua eliminada.")
    
    # 3. Crear una carpeta de migraciones completamente limpia
    os.makedirs(migrations_dir, exist_ok=True)
    with open(os.path.join(migrations_dir, '__init__.py'), 'w') as f:
        pass
    print("✨ Entorno de migraciones preparado.")

    # 4. Ejecutar los comandos de Django en el orden estricto
    print("\n⚙️ Generando esquemas para el modelo de usuario personalizado...")
    os.system("python manage.py makemigrations trading")
    
    print("\n⚙️ Aplicando las migraciones a la nueva base de datos...")
    os.system("python manage.py migrate")

    print("\n✅ ¡Problema solucionado! La estructura de la base de datos ahora es compatible con tu código.")

if __name__ == '__main__':
    fix_database()