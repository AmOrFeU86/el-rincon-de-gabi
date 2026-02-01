"""
Script para añadir los videos nuevos a la base de datos
"""
from database import SessionLocal
from models import Tema, Video
import uuid

def add_videos():
    session = SessionLocal()

    try:
        # 1. Crear tema "Introducción a Agentes de IA" si no existe
        tema_intro = session.query(Tema).filter_by(slug='introduccion-agentes').first()
        if not tema_intro:
            tema_intro = Tema(
                id=str(uuid.uuid4()),
                slug='introduccion-agentes',
                titulo='Introducción a Agentes de IA',
                descripcion='Aprende los conceptos básicos de agentes de IA y crea tu primer agente en Python',
                orden=0
            )
            session.add(tema_intro)
            print("Tema 'Introduccion a Agentes de IA' creado")

        # 2. Obtener tema "MCP y Herramientas"
        tema_mcp = session.query(Tema).filter_by(slug='mcp-herramientas').first()
        if not tema_mcp:
            print("ERROR: Tema 'mcp-herramientas' no encontrado")
            return

        # Renombrar tema MCP a algo más general
        tema_mcp.titulo = 'Herramientas y Protocolos'
        tema_mcp.descripcion = 'Tools, RAG y MCP: cómo conectar tu agente con el mundo real'

        # 3. Obtener tema "Claude Code"
        tema_claude = session.query(Tema).filter_by(slug='claude-code').first()
        if not tema_claude:
            print("ERROR: Tema 'claude-code' no encontrado")
            return

        tema_claude.descripcion = 'Aprende a usar Claude Code, el asistente de IA para programación'

        # Videos a añadir
        videos = [
            # Video 1: Agente IA básico
            {
                'tema': tema_intro,
                'youtube_id': 'BOZFN1enB6E',
                'titulo': 'Crea tu Primer Agente de IA en Python (Gratis con OpenRouter)',
                'descripcion': """En este video aprenderás a crear un agente de IA simple en Python usando OpenRouter y modelos LLM gratuitos.

✅ Usar una API Key paso a paso
✅ Qué es un LLM y cómo llamarlo desde Python
✅ Cómo escribir prompts básicos
✅ Cómo usar modelos gratuitos con OpenRouter (Mistral, etc.)

Trabajamos con un script sencillo en Python para enviar mensajes a un modelo de lenguaje y recibir respuestas. Ideal para principiantes en IA, desarrolladores Python y personas que quieren entender cómo funcionan los agentes de IA desde dentro.

Código del video (GitHub): https://github.com/AmOrFeU86/simple-ai-agent

Tecnologías usadas: Python, Requests, OpenRouter, Modelos LLM gratuitos (como Mistral)""",
                'tags': 'Clave API, OpenRouter, Script Python, IA gratuita, Modelo gratis, Tutorial IA, Python IA, Crear API, Inteligencia Artificial',
                'orden': 1
            },
            # Video 2: Tools
            {
                'tema': tema_mcp,
                'youtube_id': '',  # No tenemos el youtube_id en el metadata
                'titulo': 'Cómo crear un agente de IA que trabaje por ti (Python)',
                'descripcion': """Aprende a construir un agente de IA que puede interactuar con el mundo real usando herramientas (tools). Los LLMs por defecto no tienen acceso a internet ni pueden realizar acciones, pero con tools pueden hacer de todo.

CONTENIDO DEL VIDEO
0:00 Demo: Agente enviando noticias a Telegram
0:31 ¿Qué son las Tools de un LLM?
0:48 Herramientas implementadas (buscador, scrapper, Telegram, bolsa, Gmail, audio, imágenes, Python, archivos)
1:59 Estructura del proyecto Python
2:38 Ejecución de herramientas (tool calls)
3:48 Inyección de fecha actual al LLM
4:18 Definición de Tools (JSON)
5:01 Demo: Buscador de internet (Tavily)
5:51 Demo: Consulta de bolsa (Yahoo Finance API)
6:35 Demo: Generación de audio (Text-to-Speech)
7:58 Herramienta AudioPlayer
9:52 Demo: Ejecución de código Python
11:04 Herramienta de archivos (leer, escribir, listar)
12:30 Demo: Envío de emails con Gmail
15:50 Demo: Generación de imágenes (Replicate + Flux)
18:25 Scrapper en tiempo real (r.jina.ai)
19:40 Demo: Noticias actuales de España
20:49 API de Telegram explicada
21:45 Demo: Envío de noticias e imágenes a Telegram

Herramientas implementadas:
• Buscador web (Tavily) - búsqueda de información
• Scrapper (r.jina.ai) - contenido en tiempo real
• Telegram - envío de mensajes, fotos, audios y documentos
• Gmail - envío de emails automatizado
• Bolsa (Yahoo Finance) - precios de acciones en tiempo real
• Text-to-Speech (Edge TTS) - generación de audios
• Generación de imágenes (Replicate + Flux)
• Ejecución de Python
• Gestión de archivos""",
                'tags': 'Agente IA Python, Tools LLM, Telegram Bot IA, Gmail automatización, Yahoo Finance API, Text to Speech Python, Generación imágenes IA, Replicate Flux, Web scrapper Python, Tavily API, Edge TTS, Automatización Python, IA en español, Tutorial agentes IA',
                'orden': 1
            },
            # Video 3: RAG
            {
                'tema': tema_mcp,
                'youtube_id': '',
                'titulo': 'Cómo crear un RAG desde cero (Python + ChromaDB)',
                'descripcion': """En este video construimos un sistema RAG (Retrieval Augmented Generation) desde cero en Python usando ChromaDB.

Verás cómo conectar un LLM con datos privados (documentos, archivos o transcripciones de YouTube) para responder preguntas con contexto real, no solo con conocimiento general.

Repositorio con el código del proyecto: https://github.com/AmOrFeU86/rag-ai-agent

CONTENIDO DEL VIDEO
0:00 Introducción
0:27 ¿Qué es RAG?
1:41 Embeddings, vectores y chunking
4:41 Estructura del proyecto en Python
5:35 Ingesta de datos en ChromaDB
9:03 Consultas con RAG
11:31 Demo en vivo
14:40 Cierre

CONCEPTOS CLAVE
- RAG (Retrieval Augmented Generation)
- Bases de datos vectoriales
- Embeddings y búsqueda semántica
- Chunking de documentos
- Contexto para LLMs

IMPLEMENTACIÓN
- ChromaDB como base de datos vectorial
- Ingesta de subtítulos (.srt)
- Chat RAG paso a paso
- Integración con OpenRouter API

Caso de uso: chat que responde preguntas sobre tus propios videos de YouTube usando transcripciones.""",
                'tags': 'rag python, retrieval augmented generation, rag desde cero, chroma db, chromadb tutorial, vector database python, embeddings python, llm datos privados, rag español, ia en español, busqueda semantica, agentes ia, llm contexto, tutorial rag python',
                'orden': 2
            },
            # Video 4: MCP práctico
            {
                'tema': tema_mcp,
                'youtube_id': '',
                'titulo': 'MCP en la práctica: cliente y servidor conectados a la Base de Datos Nacional de Subvenciones',
                'descripcion': """En este video muestro un ejemplo práctico de cómo crear e implementar un servidor MCP (Model Context Protocol) en Python conectado a una API pública real.

La API utilizada es el Sistema Nacional de Publicidad de Subvenciones y Ayudas Públicas (BDNS) de España, una API gratuita que no requiere autenticación ni API key y que cuenta con documentación Swagger y especificación OpenAPI.

Web oficial del Sistema Nacional de Publicidad de Subvenciones: https://www.infosubvenciones.es/bdnstrans/GE/es/inicio

A lo largo del video se muestra:
- Por qué esta API es ideal para crear un MCP
- Cómo estructurar un servidor MCP en Python
- Definición de tools MCP como buscar ayudas, detalle de ayuda, últimas ayudas, regiones y tipos de beneficiario
- Uso de Pydantic para modelar los datos
- Implementación del cliente MCP y conexión con la API REST
- Ejecución del MCP desde un agente en Python
- Uso del servidor MCP directamente desde Cloud Code mediante transporte STDIO

Repositorios del proyecto:
- Servidor MCP (BDNS): https://github.com/AmOrFeU86/bdns-mcp
- Cliente MCP: https://github.com/AmOrFeU86/mcp-client

CONTENIDO DEL VIDEO
0:00 Introducción y objetivo del video
0:25 API de subvenciones y ayudas públicas de España
0:49 Por qué usar esta API (gratuita y sin API key)
1:02 Swagger y OpenAPI
1:36 Arquitectura MCP: cliente y servidor
2:10 Dependencias usadas en el proyecto
2:36 Implementación del servidor MCP
2:46 Definición de tools (List Tools)
3:40 Ejecución de tools y llamadas internas
4:08 API client y endpoints
5:01 Detalle de ayuda y endpoints específicos
6:11 Estructura del proyecto y modelos
6:18 Inicio de la demo práctica
6:32 Cliente MCP y uso desde Python
6:50 Ejemplo: últimas ayudas
7:25 Ejemplo: detalle de una ayuda
8:04 Ejemplo: búsqueda por región y beneficiario
9:01 Integración del MCP en Cloud Code
9:21 Comando para añadir el servidor MCP
9:48 Uso del MCP desde Cloud Code
10:42 Conclusiones""",
                'tags': 'mcp, model context protocol, mcp python, api publica españa, subvenciones españa, ayudas publicas, agentes ia, ia tools, cloud code, openapi, swagger, pydantic, mcp server, mcp client, automatizacion ia, ia con apis',
                'orden': 3
            },
            # Video 5: Claude Code
            {
                'tema': tema_claude,
                'youtube_id': '',
                'titulo': 'Claude Code explicado | Instalación, comandos y demo práctica en Python',
                'descripcion': """En este video explico qué es Claude Code, el asistente de IA de Anthropic orientado a programación, y por qué creo que es una opción muy interesante frente a otros asistentes como GitHub Copilot, Cursor o Windsurf.

Veremos qué es Claude Code, cómo se diferencia de otros agentes de IA, su precio, cómo instalarlo en Windows de forma nativa y cómo se utiliza tanto desde la línea de comandos como desde editores como Visual Studio Code o IntelliJ.

También hago un repaso detallado a los comandos más importantes de Claude Code (init, clear, compact, memory, adddir, models, exit, etc.) y explico cómo afectan al contexto, rendimiento y consumo de tokens.

Finalmente, realizo una demo práctica real en la que creo desde cero una aplicación CLI en Python para gestionar tareas pendientes, utilizando Typer y guardando los datos en un archivo JSON, mostrando cómo Claude Code trabaja de forma autónoma, detecta errores y los corrige.

CONTENIDO DEL VIDEO
0:00 Introducción
0:28 ¿Qué es Claude Code?
1:17 Evolución de asistentes de programación (ChatGPT, Copilot, agentes IA)
2:15 Diferencias entre Claude Code y otros asistentes
3:03 Precio y planes (Pro y Max)
3:45 Instalación de Claude Code en Windows
4:48 Primera ejecución y permisos
5:08 Comandos principales y ayuda
6:43 Comando init y CLAUDE.md
7:20 Clear vs Compact y gestión del contexto
8:53 Uso del comando memory
9:28 adddir y trabajo con múltiples carpetas
10:18 Modelos disponibles: Opus, Sonnet y Haiku
11:08 Límites de uso y consumo
12:27 Demo: creación de una CLI en Python
14:03 Ejecución y pruebas automáticas
15:37 Detección y corrección de errores
17:01 Revisión del código generado
18:05 Uso manual de la aplicación CLI
19:13 Conclusiones y próximos pasos

CONCEPTOS CLAVE
- Claude Code
- Agentes de IA para programación
- Gestión de contexto y tokens
- Modelos Opus, Sonnet y Haiku
- Automatización desde línea de comandos
- CLI en Python""",
                'tags': 'claude code, anthropic, agentes ia, ia programación, asistente ia, claude opus, claude sonnet, cli ia, python cli, typer python, herramientas ia, ia para developers, claude code español',
                'orden': 1
            },
            # Video 6: Slash commands
            {
                'tema': tema_claude,
                'youtube_id': '',
                'titulo': 'Todos los comandos de Claude Code explicados | Guía práctica',
                'descripcion': """En este video hago un repaso completo y práctico a todos los "/commands" (comandos de barra) disponibles en Claude Code, explicando para qué sirve cada uno y en qué situaciones es más útil.

Comenzamos viendo los comandos fundamentales como init, adddir, memory, context, clear y compact, y cómo influyen directamente en la gestión del contexto y el consumo de tokens.

A continuación, repasamos comandos avanzados como fork, resume, rename y rewind para trabajar con múltiples sesiones y ramas de conversación de forma eficiente.

También exploro en detalle toda la configuración de Claude Code: cambio de modelos (Opus, Sonnet y Haiku), permisos, hooks, MCPs, plugins, estilos de salida, temas, privacidad y configuración del terminal.

Finalmente, revisamos comandos de diagnóstico y uso como help, doctor, status, usage, stats, skills, release notes, tareas en segundo plano, integración con GitHub, VS Code, Slack, móvil, exportación de conversaciones y opciones de cuenta.

CONTENIDO DEL VIDEO
0:00 Introducción
0:02 ¿Qué son los slash commands de Claude Code?
0:27 Comando init y archivo cloud.md
0:54 adddir y trabajo con múltiples directorios
1:19 memory y persistencia de información
1:32 context y consumo de tokens
1:56 clear vs compact
2:21 fork y trabajo con ramas
2:47 resume y recuperación de sesiones
3:13 rename de conversaciones
3:41 rewind en la misma sesión
3:57 exit y plan
4:08 config y cambio de modelos
4:33 Modelos Sonnet, Opus y Haiku
4:45 permissions, hooks y MCPs
5:07 plugins y configuración compartida
5:39 output style y learning mode
6:04 status line, theme y editor
6:33 privacidad y conexión remota
6:51 terminal setup y help
7:22 doctor, status y usage
7:56 stats, skills y release notes
8:30 to-do, tasks y procesos en segundo plano
9:02 Integraciones con GitHub y seguridad
9:24 agents, Chrome y VS Code
9:51 Slack, móvil y exportación
10:06 login, upgrade y feedback
10:29 Cierre y conclusiones

CONCEPTOS CLAVE
- Claude Code
- Slash commands
- Gestión de contexto y tokens
- Sesiones y ramas de conversación
- Modelos Opus, Sonnet y Haiku
- Configuración avanzada
- Automatización desde terminal""",
                'tags': 'claude code, cloud code, slash commands, comandos claude, agentes ia, ia programación, asistente ia, claude opus, claude sonnet, cli ia, herramientas ia, ia para developers, claude code español',
                'orden': 2
            }
        ]

        # Añadir videos
        for video_data in videos:
            # Verificar si el video ya existe (por titulo)
            existing = session.query(Video).filter_by(
                tema_id=video_data['tema'].id,
                titulo=video_data['titulo']
            ).first()

            if not existing:
                video = Video(
                    tema_id=video_data['tema'].id,
                    youtube_id=video_data['youtube_id'],
                    titulo=video_data['titulo'],
                    descripcion=video_data['descripcion'],
                    tags=video_data['tags'],
                    orden=video_data['orden']
                )
                session.add(video)
                print(f"Video añadido: {video_data['titulo'][:50]}...")
            else:
                print(f"Video ya existe: {video_data['titulo'][:50]}...")

        session.commit()
        print("\nOK - Todos los videos han sido procesados")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    add_videos()
