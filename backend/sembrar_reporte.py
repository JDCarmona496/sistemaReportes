from app.database import SessionLocal
from app.models.report import Report
import json

# TU QUERY OPTIMIZADA (Nota los :variables)
SQL_PACIENTES = """
SELECT
    (ROW_NUMBER() OVER (ORDER BY pa.fecha ASC) + :ultimo_id) AS id,
    pa.paciente_cod AS noIngreso,
    CONCAT_WS(' ', pa.nom1, pa.ape1) AS nombre,
    COALESCE(TO_CHAR(pa.nacio, 'YYYY-MM-DD'), '2000-01-01') AS fechaNac,
    pa.tipodcto_cod as tipoDocum,
    pa.nit AS numDocum,
    pa.edad,
    CASE 
        WHEN pa.est_civil = 'S' THEN 'Soltero'
        WHEN pa.est_civil = 'C' THEN 'Casado'
        ELSE 'Indeterminado'
    END AS estadoCivil,
    pa.direccion as direccionResidencia,
    pa.sexo AS genero,
    pa.email,
    c.razon as razonSocialCliente,
    c.nit as nitCliente,
    c.contrato as noContratoCliente,
    CASE 
        WHEN c.razon = 'EMSSANAR EPS SUBSIDIADO' THEN 'Plan de beneficios en salud financiado con UPC'
        ELSE c.razon 
    END AS planBeneficioCliente,
    c.nombre as regimenCliente
FROM paciente pa
    LEFT JOIN clientes c ON c.clte_codigo = pa.clte_codigo
WHERE 
    pa.fecha BETWEEN :fecha_inicio AND :fecha_fin
    AND pa.paciente_cod IN :lista_pacientes
"""

# LA CONFIGURACIÓN DEL MÓDULO (Esto leerá el Frontend)
CONFIG_PARAMS = [
    {
        "name": "fecha_inicio",
        "type": "date",
        "label": "Fecha Inicial"
    },
    {
        "name": "fecha_fin",
        "type": "date",
        "label": "Fecha Final"
    },
    {
        "name": "ultimo_id",
        "type": "number",
        "label": "Iniciar consecutivo en"
    }
]

def crear_reporte_inicial():
    db = SessionLocal()
    
    # Verificar si ya existe
    existe = db.query(Report).filter(Report.title == "Reporte General Pacientes").first()
    if existe:
        print("El reporte ya existe, borrando y creando de nuevo...")
        db.delete(existe)
        db.commit()

    nuevo_reporte = Report(
        title="Reporte General Pacientes",
        description="Reporte masivo basado en CSV de ingresos y rango de fechas.",
        sql_query=SQL_PACIENTES,
        params_config=CONFIG_PARAMS, # Aquí guardamos la config del módulo
        requires_file=True,          # Importante: Le dice al front que pida CSV
        is_active=True
    )

    db.add(nuevo_reporte)
    db.commit()
    print("✅ Reporte insertado correctamente con su configuración.")
    db.close()

if __name__ == "__main__":
    crear_reporte_inicial()