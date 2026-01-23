from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings  # <--- IMPORTANTE: Aquí traemos la config segura

# Creamos el motor usando la URL que viene del .env (vía settings)
engine = create_engine(settings.DATABASE_URL)

# Crea una "fábrica" de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para crear nuestros modelos
Base = declarative_base()


# Dependencia para inyectar la BD en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
