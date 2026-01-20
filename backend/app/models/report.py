from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Aquí va tu consulta SQL con los placeholders (:fecha_inicio, :lista_pacientes)
    sql_query = Column(Text, nullable=False)
    
    # AQUÍ ESTÁ LA MAGIA DEL MÓDULO:
    # Guardaremos la definición de los inputs que necesita el reporte.
    # Ejemplo: [{"name": "fecha_inicio", "type": "date", "label": "Fecha Desde"}]
    params_config = Column(JSON, default=[])
    
    # Una bandera rápida para saber si el frontend debe mostrar la caja de "Subir Archivo"
    requires_file = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)