from fastapi import APIRouter, Depends
from app.api import deps
from app.core.lis import verificar_conexion_lis

router = APIRouter()

@router.get("/health/lis")
def check_lis_status(
    current_user = Depends(deps.get_current_user) # Solo usuarios logueados pueden ver el estado
):
    """
    Verifica la conectividad con el servidor LIS a través de la VPN.
    """
    online, mensaje = verificar_conexion_lis()
    
    return {
        "status": "ok" if online else "error",
        "message": mensaje,
        "service": "LIS Database"
    }