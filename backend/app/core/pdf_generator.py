from reportlab.lib.pagesizes import LETTER, LEGAL, A3, A2, landscape, portrait
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
import os
import re
import traceback

# ==========================================
#  LÓGICA 1: REPORTE TIPO TABLA (SÁBANA)
# ==========================================


def calcular_config_tabla(num_cols):
    """Decide tamaño de hoja según columnas."""
    if num_cols < 8:
        return (LETTER, 10, 12)
    elif num_cols <= 15:
        return (landscape(LEGAL), 8, 10)
    elif num_cols <= 30:
        return (landscape(A3), 7, 8)
    else:
        return (landscape(A2), 6, 7)


def calcular_anchos(datos, columnas, ancho_disponible):
    """Calcula anchos proporcionales."""
    try:
        pesos = {col: len(str(col)) for col in columnas}
        for fila in datos[:50]:
            for col in columnas:
                val = str(fila.get(col, "") or "")
                largo = min(len(val), 40)
                if largo > pesos[col]:
                    pesos[col] = largo
        total = sum(pesos.values()) or 1
        return [(pesos[c] / total) * ancho_disponible for c in columnas]
    except:
        return [ancho_disponible / len(columnas)] * len(columnas)


def crear_pdf_tabla(datos, titulo, filepath):
    """Genera PDF estilo Excel/Grilla."""
    todas = list(datos[0].keys())
    cols = [c for c in todas if c.lower() != "id"]

    page_size, font_size, leading = calcular_config_tabla(len(cols))
    margen = 0.5 * cm

    doc = SimpleDocTemplate(
        filepath,
        pagesize=page_size,
        rightMargin=margen,
        leftMargin=margen,
        topMargin=margen,
        bottomMargin=margen,
    )

    styles = getSampleStyleSheet()
    estilo_celda = ParagraphStyle(
        "C",
        parent=styles["Normal"],
        fontSize=font_size,
        leading=leading,
        splitLongWords=True,
    )
    estilo_header = ParagraphStyle(
        "H",
        parent=estilo_celda,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=colors.whitesmoke,
    )

    data = [[Paragraph(str(c).upper().replace("_", " "), estilo_header) for c in cols]]
    for fila in datos:
        data.append([Paragraph(str(fila.get(c, "") or ""), estilo_celda) for c in cols])

    ancho_util = page_size[0] - (2 * margen)
    anchos = calcular_anchos(datos, cols, ancho_util)

    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    elements = [Paragraph(titulo, styles["Heading1"]), Spacer(1, 0.5 * cm), t]
    doc.build(elements)


# ==========================================
#  LÓGICA 2: REPORTE TIPO FICHA (UNO POR HOJA)
# ==========================================


def crear_pdf_ficha(datos, titulo, filepath):
    """Genera PDF estilo Resultado Médico (1 reg por página)."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=LETTER,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    estilo_label = ParagraphStyle(
        "L", parent=styles["Normal"], fontName="Helvetica-Bold", textColor=colors.gray
    )

    elements = []

    for i, fila in enumerate(datos):
        # Título del reporte en cada hoja
        elements.append(Paragraph(titulo, styles["Heading1"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Subtítulo (Nombre del paciente o ID)
        desc = fila.get("nombre") or fila.get("paciente") or f"Registro #{i+1}"
        elements.append(Paragraph(f"📌 {str(desc).upper()}", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * cm))

        # Tabla Vertical
        data_tabla = []
        cols = [k for k in fila.keys() if k.lower() != "id"]

        for col in cols:
            label = col.replace("_", " ").title()
            valor = str(fila[col]) if fila[col] is not None else ""
            data_tabla.append(
                [Paragraph(label, estilo_label), Paragraph(valor, styles["Normal"])]
            )

        t = Table(data_tabla, colWidths=[6 * cm, 10 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("Padding", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(t)
        elements.append(Spacer(1, 1 * cm))
        elements.append(PageBreak())  # <--- EL SECRETO: Salto de página

    doc.build(elements)


# ==========================================
#  CONTROLADOR PRINCIPAL (DISPATCHER)
# ==========================================


def generar_pdf_universal(datos, titulo, usuario_id, layout_type="tabla"):
    """
    Función maestra que decide qué diseño usar.
    layout_type: 'tabla' | 'ficha'
    """
    if not datos:
        return None

    # Preparar ruta
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    nombre_limpio = re.sub(r'[\\/*?:"<>|]', "", titulo.replace(" ", "_"))
    nombre_archivo = f"{layout_type.capitalize()}_{usuario_id}_{nombre_limpio}.pdf"
    filepath = os.path.join(output_dir, nombre_archivo)

    try:
        print(f"🎨 Generando PDF con diseño: {layout_type.upper()}")

        if layout_type == "ficha":
            crear_pdf_ficha(datos, titulo, filepath)
        else:
            # Por defecto usamos tabla
            crear_pdf_tabla(datos, titulo, filepath)

        return f"/static/reports/{nombre_archivo}"

    except Exception as e:
        print(f"❌ Error Generando PDF: {e}")
        traceback.print_exc()
        return None
