from pydantic import BaseModel

# Esto define qué le devolvemos al usuario cuando se loguea bien
class Token(BaseModel):
    access_token: str
    token_type: str

# Esto es para decodificar el token internamente (lo usaremos después)
class TokenPayload(BaseModel):
    sub: str | None = None