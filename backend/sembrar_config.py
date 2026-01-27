from app.database import SessionLocal
from app.models.config import SystemSetting


def init_settings():
    db = SessionLocal()

    settings = [
        {
            "key": "company_name",
            "value": "BIOLAB S.A.S",
            "description": "Nombre de la empresa en reportes",
            "category": "general",
        },
        {
            "key": "company_address",
            "value": "Calle 123 #45-67, Palmira",
            "description": "Dirección en encabezados",
            "category": "general",
        },
        {
            "key": "report_footer",
            "value": "Este documento es confidencial.",
            "description": "Texto al pie del PDF",
            "category": "reportes",
        },
        {
            "key": "maintenance_mode",
            "value": "false",
            "description": "Activar modo mantenimiento (true/false)",
            "category": "sistema",
        },
        {
            "key": "contact_email",
            "value": "soporte@biolab.com",
            "description": "Email de contacto",
            "category": "general",
        },
        {
            "key": "sidebar_color",
            "value": "#1e3a8a",
            "description": "Color de fondo del menú lateral (Hex)",
            "category": "visual",
        },
        {
            "key": "app_title",
            "value": "BIOLAB System",
            "description": "Título en la pestaña del navegador",
            "category": "visual",
        },
        {
            "key": "navbar_title",
            "value": "Dashboard",
            "description": "Título en la barra superior blanca",
            "category": "visual",
        },
    ]

    for item in settings:
        exists = (
            db.query(SystemSetting).filter(SystemSetting.key == item["key"]).first()
        )
        if not exists:
            setting = SystemSetting(**item)
            db.add(setting)
            print(f"➕ Agregado: {item['key']}")

    db.commit()
    db.close()


if __name__ == "__main__":
    init_settings()
