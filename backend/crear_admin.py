from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def crear_superusuario():
    db = SessionLocal()

    email = "admin@example.com"
    password = "admin"

    # Verificar si existe
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"⚠️ El usuario {email} ya existe. Borrando y recreando...")
        db.delete(user)
        db.commit()

    # Crear nuevo Admin
    admin_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name="Administrador del Sistema",
        is_active=True,
        is_superuser=True,  # <--- CRÍTICO: Esto te da los poderes
    )

    db.add(admin_user)
    db.commit()
    print("✅ Superusuario creado exitosamente.")
    print(f"📧 User: {email}")
    print(f"🔑 Pass: {password}")
    db.close()


if __name__ == "__main__":
    crear_superusuario()
