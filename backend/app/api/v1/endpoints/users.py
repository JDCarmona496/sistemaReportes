from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas import user as user_schema

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener datos del usuario logueado actual.
    """
    return current_user