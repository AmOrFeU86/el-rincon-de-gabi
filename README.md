# El Rincón de Gabi

Web educativa complementaria al canal de YouTube sobre agentes de IA.

## Stack

- **Frontend**: Astro + Alpine.js + Tailwind CSS
- **Backend**: Python + FastAPI + SQLAlchemy
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **LLM**: Gemini 2.5 Flash (via OpenRouter)

## Estructura

```
el-rincon-de-gabi/
├── frontend/          # Astro app
│   ├── src/
│   │   ├── components/
│   │   ├── layouts/
│   │   └── pages/
│   │       ├── index.astro
│   │       └── temas/
│   │           └── [slug].astro
│   └── package.json
├── backend/           # FastAPI
│   ├── main.py
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # DB configuration
│   ├── crud.py           # DB operations
│   ├── educativo.db      # SQLite database
│   ├── ejercicios_backup/ # JSON backups
│   └── requirements.txt
└── .env.example
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Migrar datos a base de datos (solo primera vez)
python migrate_to_db.py

# Configurar variable de entorno
set OPENROUTER_API_KEY=tu-api-key

# Iniciar servidor
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /temas | Lista todos los temas |
| GET | /temas/{slug} | Detalle de tema (con videos y ejercicios) |
| GET | /ejercicios/{id} | Detalle de ejercicio individual |
| POST | /verificar | Verifica respuesta escrita con IA |

## Tipos de ejercicios

1. **Quiz** - Preguntas de opción múltiple (verificación local)
2. **Código** - Completar código con dropdowns/inputs (verificación local)
3. **Escrito** - Respuesta libre (verificación con Gemini)

## Arquitectura de Temas

La aplicación está organizada en **temas**, cada uno con:
- Descripción y teoría
- Uno o más videos de YouTube
- Múltiples ejercicios (quiz, código, escrito)

### Añadir contenido

Para añadir temas o ejercicios, modifica `backend/migrate_to_db.py` y ejecuta la migración:

```python
# Añadir un nuevo tema en TEMAS_CONFIG
{
    "id": "tema-005",
    "slug": "mi-tema",
    "titulo": "Mi Tema",
    "descripcion": "Descripción del tema",
    "orden": 5,
    "videos": [
        {"youtube_id": "abc123", "titulo": "Video 1", "orden": 1}
    ],
    "ejercicios": ["ejercicio-id"]
}
```

Luego ejecuta:
```bash
python migrate_to_db.py
```

### Migración a PostgreSQL

Para producción, solo cambia la conexión en `backend/database.py`:

```python
# De SQLite:
DATABASE_URL = "sqlite:///educativo.db"

# A PostgreSQL:
DATABASE_URL = "postgresql://user:password@localhost/educativo"
```
