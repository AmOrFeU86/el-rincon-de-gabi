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
from models import TemaListResponse, TemaDetailResponse, Video
from sqlalchemy import or_


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
LLM_MODEL = "x-ai/grok-4.1-fast"


# ============== Models ==============

class RespuestaEscrita(BaseModel):
    pregunta: str
    contexto: Optional[str] = ""
    respuesta: str


class VerificarRequest(BaseModel):
    tipo: str
    ejercicio_id: str
    respuestas: list[RespuestaEscrita]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


# ============== Helper Functions ==============

def limpiar_enlaces_html(text: str) -> str:
    """Convierte enlaces HTML malformados a formato Markdown correcto (por seguridad)"""
    import re

    if not text:
        return text

    # Patrón 1: href="URL">Texto (sin etiqueta de cierre) - fallback por si acaso
    text = re.sub(r'href="([^"]+)">([^\n]+?)(?=\n|href=|$)', r'[\2](\1)', text)

    # Patrón 2: <a href="URL">Texto</a> - fallback por si acaso
    text = re.sub(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', text)

    return text


def buscar_videos_por_keywords(keywords: list[str], db: Session, limit: int = 5) -> list[dict]:
    """Busca videos en la BD usando keywords en titulo, descripcion y tags"""
    if not keywords:
        return []

    # Construir condiciones OR para cada keyword
    conditions = []
    for keyword in keywords:
        keyword_lower = f"%{keyword.lower()}%"
        conditions.extend([
            Video.titulo.ilike(keyword_lower),
            Video.descripcion.ilike(keyword_lower),
            Video.tags.ilike(keyword_lower)
        ])

    # Buscar videos que coincidan con alguna condición
    videos = db.query(Video).filter(or_(*conditions)).limit(limit).all()

    # Formatear resultados
    resultados = []
    for video in videos:
        resultados.append({
            "titulo": video.titulo,
            "descripcion": video.descripcion[:500] if video.descripcion else "",  # Limitar a 500 chars
            "youtube_id": video.youtube_id,
            "tags": video.tags
        })

    return resultados


def obtener_url_tema_interno(slug_tema: str) -> str:
    """Devuelve URL interna del sitio web según el slug del tema"""
    base_url = "http://localhost:3000"  # Puerto del frontend

    temas_map = {
        # Temas principales del curso
        "memoria-agentes": f"{base_url}/temas/memoria-agentes",
        "comunicacion-agentes": f"{base_url}/temas/comunicacion-agentes",
        "claude-code": f"{base_url}/temas/claude-code",
        "mcp-herramientas": f"{base_url}/temas/mcp-herramientas",
        "introduccion-agentes": f"{base_url}/temas/introduccion-agentes",

        # Sinónimos y variaciones comunes - Memoria
        "memoria": f"{base_url}/temas/memoria-agentes",
        "memoria-corto-plazo": f"{base_url}/temas/memoria-agentes",
        "memoria-largo-plazo": f"{base_url}/temas/memoria-agentes",
        "memoria-episodica": f"{base_url}/temas/memoria-agentes",
        "memoria-semantica": f"{base_url}/temas/memoria-agentes",

        # Sinónimos - Comunicación
        "comunicacion": f"{base_url}/temas/comunicacion-agentes",
        "protocolo-a2a": f"{base_url}/temas/comunicacion-agentes",
        "a2a": f"{base_url}/temas/comunicacion-agentes",

        # Sinónimos - Claude Code
        "claude": f"{base_url}/temas/claude-code",
        "cli": f"{base_url}/temas/claude-code",

        # Sinónimos - MCP y Herramientas (incluye RAG)
        "mcp": f"{base_url}/temas/mcp-herramientas",
        "herramientas": f"{base_url}/temas/mcp-herramientas",
        "model-context-protocol": f"{base_url}/temas/mcp-herramientas",
        "rag": f"{base_url}/temas/mcp-herramientas",
        "rag-vectores": f"{base_url}/temas/mcp-herramientas",
        "vectores": f"{base_url}/temas/mcp-herramientas",
        "embeddings": f"{base_url}/temas/mcp-herramientas",

        # Aliases adicionales
        "agentes": f"{base_url}/temas/memoria-agentes",
        "agentes-ia": f"{base_url}/temas/introduccion-agentes",
        "multi-agente": f"{base_url}/temas/comunicacion-agentes",
        "introduccion": f"{base_url}/temas/introduccion-agentes",
    }

    slug_lower = slug_tema.lower()
    if slug_lower in temas_map:
        return temas_map[slug_lower]

    return f"{base_url}/"  # Página principal si no encuentra el tema


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


@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY no configurada")

    # Definición de las tools disponibles
    tools = [
        {
            "type": "function",
            "function": {
                "name": "buscar_videos",
                "description": "Busca videos del canal relacionados con ciertos temas o keywords. Usa esta función cuando el usuario pregunte sobre temas específicos como memoria, RAG, MCP, Claude Code, tools, agentes, etc. Extrae keywords relevantes de la pregunta del usuario.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de keywords o temas relacionados con la pregunta. Por ejemplo: ['memoria', 'conversaciones'], ['rag', 'vectores'], ['mcp', 'herramientas'], etc."
                        }
                    },
                    "required": ["keywords"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "redirigir_temas_internos",
                "description": "OBLIGATORIO: Usa esta función cuando el usuario pregunte sobre cualquier tema del curso. NO generes URLs manualmente. Temas: memoria en agentes, comunicación entre agentes, Claude Code, MCP/herramientas (incluye RAG, vectores, embeddings), introducción a agentes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "slug_tema": {
                            "type": "string",
                            "description": "Slug o keyword del tema. Ejemplos: 'memoria', 'memoria-agentes', 'comunicacion', 'claude-code', 'mcp', 'rag', 'rag-vectores', 'vectores', 'embeddings', 'herramientas', 'agentes', 'introduccion'. La función mapea automáticamente sinónimos al tema correcto."
                        }
                    },
                    "required": ["slug_tema"]
                }
            }
        }
    ]

    # Añadir mensaje del sistema al inicio si no existe
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    # Si no hay mensaje del sistema, añadirlo
    if not messages or messages[0]["role"] != "system":
        system_message = {
            "role": "system",
            "content": "Eres un asistente experto en agentes de IA, programación y tecnología. "
                      "Ayudas a los estudiantes de 'El Rincón de Gabi' a aprender sobre estos temas. "
                      "\n\n=== FORMATO DE ENLACES - REGLA ABSOLUTA ===\n"
                      "OBLIGATORIO: Todos los enlaces DEBEN seguir EXACTAMENTE este formato Markdown:\n"
                      "[texto descriptivo](https://url-completa.com)\n\n"
                      "EJEMPLOS CORRECTOS:\n"
                      "- [Documentación de Anthropic](https://docs.anthropic.com)\n"
                      "- [Guía de inicio rápido](https://docs.anthropic.com/quickstart)\n\n"
                      "PROHIBIDO - NUNCA uses estos formatos:\n"
                      "❌ href=\"https://url.com\">Texto\n"
                      "❌ <a href=\"https://url.com\">Texto</a>\n"
                      "❌ https://url.com (URL sola)\n"
                      "❌ Cualquier fragmento de HTML\n\n"
                      "Si necesitas incluir múltiples enlaces, usa una lista Markdown:\n"
                      "- [Enlace 1](https://url1.com)\n"
                      "- [Enlace 2](https://url2.com)\n"
                      "\n\n=== USO DE HERRAMIENTAS - CRÍTICO ===\n"
                      "NUNCA generes URLs a temas del curso directamente. SIEMPRE usa las herramientas.\n"
                      "PROHIBIDO generar URLs como elrincondelgabi.com/... o localhost/... manualmente.\n\n"
                      "Herramientas disponibles:\n"
                      "1. buscar_videos: Para buscar videos específicos del canal cuando pregunten sobre temas concretos\n"
                      "2. redirigir_temas_internos: OBLIGATORIO para cualquier mención de temas del curso (memoria, comunicación, MCP, RAG, vectores, Claude Code, agentes, etc.)\n"
                      "\nUSO OBLIGATORIO DE HERRAMIENTAS:\n"
                      "- Cuando el usuario pregunte sobre temas como RAG, memoria, MCP, agentes, etc. → DEBES llamar a redirigir_temas_internos\n"
                      "- Para buscar contenido específico del canal → buscar_videos\n"
                      "- NUNCA inventes o escribas URLs manualmente. SIEMPRE usa las funciones.\n"
        }
        messages.insert(0, system_message)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Primera llamada al LLM con tools
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "tools": tools,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()

        assistant_message = data["choices"][0]["message"]

        # Verificar si el LLM quiere llamar a una tool
        if assistant_message.get("tool_calls"):
            tool_call = assistant_message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])

            # Ejecutar la tool solicitada
            if function_name == "buscar_videos":
                keywords = function_args.get("keywords", [])
                videos_encontrados = buscar_videos_por_keywords(keywords, db)

                # Formatear los resultados
                if videos_encontrados:
                    videos_text = "\n\n".join([
                        f"**{v['titulo']}**\n{v['descripcion']}\nTags: {v['tags']}"
                        for v in videos_encontrados
                    ])
                    tool_response = f"Videos encontrados:\n\n{videos_text}"
                else:
                    tool_response = "No se encontraron videos relacionados con esos temas."

            elif function_name == "redirigir_temas_internos":
                slug_tema = function_args.get("slug_tema", "")
                url = obtener_url_tema_interno(slug_tema)
                if url.endswith("/"):
                    # Es la página principal
                    tool_response = f"Puedes ver todos los temas disponibles en: {url}"
                else:
                    # Es un tema específico
                    tool_response = f"Tema específico disponible en: {url}"
            else:
                tool_response = f"Función {function_name} no reconocida."

            # Añadir el mensaje del asistente con tool_call y la respuesta de la tool
            messages.append({
                "role": "assistant",
                "content": assistant_message.get("content"),
                "tool_calls": assistant_message["tool_calls"]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": function_name,
                "content": tool_response
            })

            # Segunda llamada al LLM con los resultados de la tool
            async with httpx.AsyncClient(timeout=30.0) as client:
                response2 = await client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": messages,
                        "tools": tools,
                        "temperature": 0.7,
                    },
                )
                response2.raise_for_status()
                data2 = response2.json()

            final_message = data2["choices"][0]["message"]["content"]
            # Limpiar enlaces HTML malformados
            final_message = limpiar_enlaces_html(final_message)
            return {"role": "assistant", "content": final_message}

        # Si no hay tool calls, devolver la respuesta directa
        content = assistant_message.get("content", "")
        # Limpiar enlaces HTML malformados
        content = limpiar_enlaces_html(content)
        return {"role": "assistant", "content": content}

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error llamando al LLM: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
