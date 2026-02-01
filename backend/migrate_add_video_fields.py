"""
Script para añadir los campos descripcion y tags a la tabla videos
"""
from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Añadir columna descripcion si no existe
        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN descripcion TEXT"))
            print("OK - Columna 'descripcion' añadida")
        except Exception as e:
            print(f"Columna 'descripcion' ya existe o error: {e}")

        # Añadir columna tags si no existe
        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN tags TEXT"))
            print("OK - Columna 'tags' añadida")
        except Exception as e:
            print(f"Columna 'tags' ya existe o error: {e}")

        conn.commit()
        print("\nOK - Migracion completada")

if __name__ == "__main__":
    migrate()
