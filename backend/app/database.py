from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse  # <--- 1. Agregamos esta librería

# ---------------------------------------------------------
# CONFIGURACIÓN DE CREDENCIALES
# ---------------------------------------------------------
DB_USER = "postgres"
DB_PASS = "12345"  # <--- Pon tu contraseña real aquí
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "reportes_db"

# 2. Codificamos la contraseña para que los símbolos no rompan la URL
encoded_password = urllib.parse.quote_plus(DB_PASS)

# 3. Construimos la URL usando la f-string con la password codificada
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crea el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Crea una "fábrica" de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para crear nuestros modelos
Base = declarative_base()

# Dependencia
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()