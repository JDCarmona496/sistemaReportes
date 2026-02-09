from fastapi import APIRouter, Depends
from app.api import deps
from app.core.lis import verificar_conexion_lis

router = APIRouter()

@router.get("/health/lis")
def check_lis_status(
    sede: str = "BIOLAB", # <--- NUEVO: Recibe ?sede=BIOSALUD desde el frontend
    current_user = Depends(deps.get_current_user) # Solo usuarios logueados
):
    """
    Verifica la conectividad con el servidor LIS a través de la VPN.
    Permite especificar la sede para probar diferentes conexiones.
    """
    # Pasamos la sede elegida al monitor de conexión
    online, mensaje = verificar_conexion_lis(sede)
    
    return {
        "status": "ok" if online else "error",
        "message": mensaje,
        "service": "LIS Database",
        "sede": sede
    }