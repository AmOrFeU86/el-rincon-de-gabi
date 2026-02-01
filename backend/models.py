from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from pydantic import BaseModel

# SQLAlchemy Models (Base de datos)
Base = declarative_base()

class Tema(Base):
    __tablename__ = 'temas'

    id = Column(String, primary_key=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    orden = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    videos = relationship("Video", back_populates="tema", cascade="all, delete-orphan")
    ejercicios = relationship("Ejercicio", back_populates="tema", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tema_id = Column(String, ForeignKey('temas.id', ondelete='CASCADE'), nullable=False, index=True)
    youtube_id = Column(String, nullable=False)
    titulo = Column(String)
    descripcion = Column(Text)  # Descripción completa del video
    tags = Column(Text)  # Tags del video (separados por comas)
    orden = Column(Integer, default=0)

    # Relación
    tema = relationship("Tema", back_populates="videos")

class Ejercicio(Base):
    __tablename__ = 'ejercicios'

    id = Column(String, primary_key=True)
    tema_id = Column(String, ForeignKey('temas.id', ondelete='CASCADE'), nullable=False, index=True)
    titulo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'quiz', 'codigo', 'escrito'
    contenido = Column(Text, nullable=False)  # JSON serializado
    orden = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    tema = relationship("Tema", back_populates="ejercicios")


# Pydantic Models (API responses)
class VideoResponse(BaseModel):
    id: int
    youtube_id: str
    titulo: str | None
    descripcion: str | None
    tags: str | None
    orden: int

    class Config:
        from_attributes = True

class EjercicioResponse(BaseModel):
    id: str
    titulo: str
    tipo: str
    preguntas: list | dict

class TemaListResponse(BaseModel):
    id: str
    slug: str
    titulo: str
    descripcion: str | None
    orden: int
    total_videos: int
    total_ejercicios: int

class TemaDetailResponse(BaseModel):
    id: str
    slug: str
    titulo: str
    descripcion: str | None
    videos: list[VideoResponse]
    ejercicios: list[EjercicioResponse]
