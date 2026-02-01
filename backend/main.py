import json
import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, get_db
from crud import get_all_temas, get_tema_by_slug, get_ejercicio_by_id
from models import TemaListResponse, TemaDetailResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (si fuera necesario)

app = FastAPI(title="El Rincón de Gabi API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "google/gemini-2.5-flash-preview"


# ============== Models ==============

class RespuestaEscrita(BaseModel):
    pregunta: str
    contexto: Optional[str] = ""
    respuesta: str


class VerificarRequest(BaseModel):
    tipo: str
    ejercicio_id: str
    respuestas: list[RespuestaEscrita]


# ============== Endpoints ==============

@app.get("/")
def root():
    return {"message": "El Rincón de Gabi API", "version": "1.0.0"}


@app.get("/temas", response_model=list[TemaListResponse])
def list_temas(db: Session = Depends(get_db)):
    temas = get_all_temas(db)
    return [
        {
            "id": t.id,
            "slug": t.slug,
            "titulo": t.titulo,
            "descripcion": t.descripcion,
            "orden": t.orden,
            "total_videos": len(t.videos),
            "total_ejercicios": len(t.ejercicios)
        }
        for t in temas
    ]


@app.get("/temas/{slug}", response_model=TemaDetailResponse)
def get_tema_detail(slug: str, db: Session = Depends(get_db)):
    tema = get_tema_by_slug(db, slug)
    if not tema:
        raise HTTPException(404, "Tema no encontrado")

    return {
        "id": tema.id,
        "slug": tema.slug,
        "titulo": tema.titulo,
        "descripcion": tema.descripcion,
        "videos": tema.videos,
        "ejercicios": [
            {
                "id": e.id,
                "titulo": e.titulo,
                "tipo": e.tipo,
                "preguntas": json.loads(e.contenido)
            }
            for e in tema.ejercicios
        ]
    }


@app.get("/ejercicios/{ejercicio_id}")
def get_ejercicio(ejercicio_id: str, db: Session = Depends(get_db)):
    ej = get_ejercicio_by_id(db, ejercicio_id)
    if not ej:
        raise HTTPException(404, "Ejercicio no encontrado")

    return {
        "id": ej.id,
        "titulo": ej.titulo,
        "tipo": ej.tipo,
        "preguntas": json.loads(ej.contenido)
    }


@app.post("/verificar")
async def verificar_respuesta(request: VerificarRequest):
    if request.tipo != "escrito":
        raise HTTPException(status_code=400, detail="Solo se verifican respuestas escritas")

    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY no configurada")

    prompt = """Eres un profesor evaluando respuestas de estudiantes sobre agentes de IA.
Para cada respuesta, evalúa del 0 al 100 según:
- Precisión técnica (40%)
- Claridad de explicación (30%)
- Uso correcto de terminología (30%)

Responde SOLO en JSON con este formato exacto:
{
  "puntuacion": <promedio de todas las respuestas>,
  "feedback": {
    "0": "<feedback breve para pregunta 1>",
    "1": "<feedback breve para pregunta 2>",
    ...
  }
}

Preguntas y respuestas a evaluar:
"""

    for i, r in enumerate(request.respuestas):
        prompt += f"\n{i+1}. Pregunta: {r.pregunta}"
        if r.contexto:
            prompt += f"\n   Contexto: {r.contexto}"
        prompt += f"\n   Respuesta del estudiante: {r.respuesta}\n"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        result = json.loads(content.strip())
        return result

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error llamando al LLM: {str(e)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parseando respuesta del LLM")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
