from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

# SQLite para desarrollo (migrar a Postgres cambiando solo esta línea)
DATABASE_URL = "sqlite:///educativo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def get_db() -> Session:
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
