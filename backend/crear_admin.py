# Este script crea un usuario admin inicial
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def init_db():
    db = SessionLocal()
    
    # Verificamos si ya existe el usuario para no duplicarlo
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if user:
        print("El usuario admin ya existe.")
        return

    print("Creando usuario administrador...")
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"), # La contraseña será admin123
        full_name="Administrador del Sistema",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    print("Usuario creado exitosamente: admin@example.com / admin123")
    db.close()

if __name__ == "__main__":
    init_db()