from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def crear_superusuario():
    db = SessionLocal()

    email = "admin@example.com"
    password = "admin"

    # Verificar si existe
    # type: ignore - Pylance se confunde con la cadena de métodos de SQLAlchemy
    user = db.query(User).filter(User.email == email).first() # type: ignore
    if user:
        print(f"⚠️ El usuario {email} ya existe. Borrando y recreando...")
        db.delete(user)
        db.commit()

    # Crear nuevo Admin
    # type: ignore - Pylance no ve el constructor mágico de SQLAlchemy
    admin_user = User(
        email=email, # type: ignore
        hashed_password=get_password_hash(password), # type: ignore
        full_name="Administrador del Sistema", # type: ignore
        is_active=True, # type: ignore
        is_superuser=True, # type: ignore
    )

    db.add(admin_user)
    db.commit()
    print("✅ Superusuario creado exitosamente.")
    print(f"📧 User: {email}")
    print(f"🔑 Pass: {password}")
    db.close()


if __name__ == "__main__":
    crear_superusuario()
