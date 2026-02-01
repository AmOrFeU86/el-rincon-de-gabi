import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Tema, Video, Ejercicio

# Definición de temas y su mapeo con ejercicios
TEMAS_CONFIG = [
    {
        "id": "tema-001",
        "slug": "memoria-agentes",
        "titulo": "Memoria en Agentes de IA",
        "descripcion": "Explora los diferentes tipos de memoria que utilizan los agentes de IA: memoria a corto plazo, largo plazo, episódica y semántica-procedimental.",
        "orden": 1,
        "videos": [
            {"youtube_id": "730iHz1RQ1s", "titulo": "Memoria a corto plazo", "orden": 1},
            {"youtube_id": "XrxjWUyAM24", "titulo": "Memoria a largo plazo", "orden": 2},
            {"youtube_id": "K-oW9vN-BPk", "titulo": "Memoria episódica", "orden": 3},
            {"youtube_id": "qUOSmuKepKI", "titulo": "Memoria semántica y procedimental", "orden": 4},
        ],
        "ejercicios": [
            "short-term-memory",
            "long-term-memory",
            "episodic-memory",
            "semantic-procedural-memory"
        ]
    },
    {
        "id": "tema-002",
        "slug": "comunicacion-agentes",
        "titulo": "Comunicación entre Agentes",
        "descripcion": "Aprende cómo los agentes de IA se comunican entre sí usando el protocolo A2A y otras técnicas de comunicación multi-agente.",
        "orden": 2,
        "videos": [
            {"youtube_id": "dQw4w9WgXcQ", "titulo": "Protocolo A2A", "orden": 1},
        ],
        "ejercicios": [
            "a2a-protocol"
        ]
    },
    {
        "id": "tema-003",
        "slug": "claude-code",
        "titulo": "Claude Code",
        "descripcion": "Domina el uso de Claude Code, la herramienta CLI oficial de Anthropic para desarrollo con Claude.",
        "orden": 3,
        "videos": [],
        "ejercicios": []
    },
    {
        "id": "tema-004",
        "slug": "mcp-herramientas",
        "titulo": "MCP y Herramientas",
        "descripcion": "Descubre el Model Context Protocol (MCP) y cómo crear herramientas personalizadas para tus agentes de IA.",
        "orden": 4,
        "videos": [
            {"youtube_id": "dQw4w9WgXcQ", "titulo": "Introducción a MCP", "orden": 1},
        ],
        "ejercicios": [
            "mcp-basics"
        ]
    }
]

def migrate():
    """Migrar ejercicios JSON a base de datos SQLAlchemy"""
    print("🚀 Iniciando migración...")

    # Crear todas las tablas
    print("📊 Creando tablas...")
    Base.metadata.create_all(bind=engine)

    # Crear sesión
    db: Session = SessionLocal()

    try:
        # Crear directorio de backup
        backup_dir = Path("ejercicios_backup")
        backup_dir.mkdir(exist_ok=True)
        print(f"📁 Directorio de backup: {backup_dir}")

        ejercicios_dir = Path("ejercicios")

        # Procesar cada tema
        for tema_config in TEMAS_CONFIG:
            print(f"\n📚 Procesando tema: {tema_config['titulo']}")

            # Crear tema
            tema = Tema(
                id=tema_config["id"],
                slug=tema_config["slug"],
                titulo=tema_config["titulo"],
                descripcion=tema_config["descripcion"],
                orden=tema_config["orden"]
            )
            db.add(tema)
            print(f"  ✅ Tema creado: {tema.slug}")

            # Agregar videos
            for video_data in tema_config["videos"]:
                video = Video(
                    tema_id=tema.id,
                    youtube_id=video_data["youtube_id"],
                    titulo=video_data["titulo"],
                    orden=video_data["orden"]
                )
                db.add(video)
                print(f"    🎥 Video agregado: {video.titulo}")

            # Agregar ejercicios
            for idx, ejercicio_id in enumerate(tema_config["ejercicios"], start=1):
                json_file = ejercicios_dir / f"{ejercicio_id}.json"

                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Crear ejercicio con contenido serializado
                    ejercicio = Ejercicio(
                        id=data["id"],
                        tema_id=tema.id,
                        titulo=data["titulo"],
                        tipo=data["tipo"],
                        contenido=json.dumps(data["preguntas"], ensure_ascii=False),
                        orden=idx
                    )
                    db.add(ejercicio)
                    print(f"    ✏️  Ejercicio agregado: {ejercicio.titulo} ({ejercicio.tipo})")

                    # Mover JSON a backup
                    backup_file = backup_dir / json_file.name
                    json_file.rename(backup_file)
                    print(f"      📦 Movido a backup: {backup_file}")
                else:
                    print(f"    ⚠️  Archivo no encontrado: {json_file}")

        # Mover agent-architecture.json a backup (no se usa)
        agent_arch_file = ejercicios_dir / "agent-architecture.json"
        if agent_arch_file.exists():
            backup_file = backup_dir / agent_arch_file.name
            agent_arch_file.rename(backup_file)
            print(f"\n📦 Movido a backup (no usado): {backup_file}")

        # Commit de la transacción
        db.commit()
        print("\n✅ Migración completada exitosamente!")

        # Mostrar resumen
        total_temas = db.query(Tema).count()
        total_videos = db.query(Video).count()
        total_ejercicios = db.query(Ejercicio).count()

        print(f"\n📈 Resumen:")
        print(f"  - Temas: {total_temas}")
        print(f"  - Videos: {total_videos}")
        print(f"  - Ejercicios: {total_ejercicios}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
