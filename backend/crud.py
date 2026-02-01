from sqlalchemy.orm import Session
from models import Tema, Ejercicio

def get_all_temas(db: Session) -> list[Tema]:
    """Obtener todos los temas ordenados"""
    return db.query(Tema).order_by(Tema.orden).all()

def get_tema_by_slug(db: Session, slug: str) -> Tema | None:
    """Obtener un tema por su slug"""
    return db.query(Tema).filter(Tema.slug == slug).first()

def get_ejercicio_by_id(db: Session, ejercicio_id: str) -> Ejercicio | None:
    """Obtener un ejercicio por su ID"""
    return db.query(Ejercicio).filter(Ejercicio.id == ejercicio_id).first()
