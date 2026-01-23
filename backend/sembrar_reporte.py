from app.database import SessionLocal
from app.models.report import Report

# QUERY MEJORADO CON VALIDACIONES
SQL_POR_LISTA = """
SELECT
    (ROW_NUMBER() OVER (ORDER BY pa.paciente_cod ASC) + %(ultimo_id)s) AS id,
    pa.paciente_cod AS noIngreso,
    CONCAT_WS(' ', pa.nom1, pa.ape1) AS nombre,
    COALESCE(TO_CHAR(pa.nacio, 'YYYY-MM-DD'), '2000-01-01') AS fechaNac,
    pa.tipodcto_cod as tipoDocum,
    pa.nit AS numDocum,
    pa.edad,
    CASE floor(random() * 3)
        WHEN 0 THEN 'Soltero'
        WHEN 1 THEN 'Casado'
        ELSE 'Divorciado'
    END AS estadoCivil,
    
    -- VALIDACIÓN DIRECCIÓN (Maneja NULL y vacíos)
    COALESCE(NULLIF(TRIM(pa.direccion), ''), 'Cra. 27 #36-42') AS direccionResidencia,
    CASE
    WHEN pa.sexo = 'M' THEN 'Masculino'
    WHEN pa.sexo = 'F' THEN 'Femenino'
    ELSE 'Otro'
    END AS genero,
    
    
    -- VALIDACIÓN EMAIL (Maneja NULL y vacíos)
    COALESCE(NULLIF(TRIM(pa.email), ''), 'radicacion.biolab@biolabdiagnostica.com') AS email,
    
    c.razon as razonSocialCliente,
    c.nit as nitCliente,
    c.contrato as noContratoCliente,
    CASE 
        WHEN c.razon = 'EMSSANAR EPS S.A.S' THEN 'Plan de beneficios en salud financiado con UPC'
        ELSE c.razon 
    END AS planBeneficioCliente,
    c.nombre as regimenCliente
FROM paciente pa
    LEFT JOIN clientes c ON c.clte_codigo = pa.clte_codigo
WHERE 
    pa.paciente_cod IN %(lista_pacientes)s
"""

PARAMS_CONFIG = [
    {
        "name": "lista_pacientes",
        "label": "Ingresos (separados por coma sin espacios ej: 80007070,80007071)",
        "type": "text",
        "placeholder": "Ej: 80007070,80007071",
        "required": True,
    },
    {
        "name": "ultimo_id",
        "label": "Iniciar consecutivo en",
        "type": "number",
        "value": 0,
        "required": True,
    },
]


def sembrar():
    db = SessionLocal()
    # Limpiamos todo para actualizar el query
    db.query(Report).delete()
    db.commit()

    nuevo_reporte = Report(
        title="Reporte por Lista (PDF/CSV)",
        description="Genera reporte validando emails y direcciones vacías.",
        sql_query=SQL_POR_LISTA,
        params_config=PARAMS_CONFIG,
        is_active=True,
    )

    db.add(nuevo_reporte)
    db.commit()
    print("✅ SQL Actualizado y reporte sembrado.")
    db.close()


if __name__ == "__main__":
    sembrar()
