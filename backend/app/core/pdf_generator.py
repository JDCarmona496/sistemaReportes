from reportlab.lib.pagesizes import LEGAL, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
import os
import re
import traceback


def calcular_anchos_proporcionales(datos, columnas, ancho_disponible):
    """
    Calcula anchos que SIEMPRE suman exactamente el ancho_disponible.
    Funciona por porcentajes/pesos, no por medidas absolutas.
    """
    if not datos or not columnas:
        return None

    try:
        # 1. Calcular 'Peso' de cada columna basado en longitud de caracteres
        # Iniciamos con el largo del título
        pesos = {col: len(str(col)) for col in columnas}

        # Muestreamos datos para ajustar el peso
        for fila in datos[:50]:
            for col in columnas:
                val = str(fila.get(col, "") or "")
                largo = len(val)
                # Nos quedamos con el valor máximo encontrado
                if largo > pesos[col]:
                    pesos[col] = largo

        # 2. Ajuste fino de pesos:
        # Penalizamos columnas muy largas (como direcciones) para que no se coman todo el espacio
        # y bonificamos columnas muy cortas (como edad/sexo) para que no desaparezcan.
        for col in columnas:
            pesos[col] = max(
                5, min(pesos[col], 50)
            )  # Mínimo 5 chars, Máximo 50 chars de peso

        # 3. Sumar pesos totales
        total_peso = sum(pesos.values())
        if total_peso == 0:
            total_peso = 1

        # 4. Repartir el ancho disponible (Regla de tres simple)
        anchos_finales = []
        for col in columnas:
            porcentaje = pesos[col] / total_peso
            ancho_exacto = ancho_disponible * porcentaje
            anchos_finales.append(ancho_exacto)

        return anchos_finales

    except Exception as e:
        print(f"⚠️ Error calculando anchos: {e}")
        return [ancho_disponible / len(columnas)] * len(columnas)


def crear_pdf_generico(datos: list, titulo_reporte: str, usuario_id: int):
    """
    Genera PDF ajustado al 100% del ancho de página, ocultando la columna ID.
    """
    if not datos:
        return None

    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)

    nombre_limpio = re.sub(r'[\\/*?:"<>|]', "", titulo_reporte.replace(" ", "_"))
    nombre_archivo = f"Reporte_{usuario_id}_{nombre_limpio}.pdf"
    filepath = os.path.join(output_dir, nombre_archivo)

    try:
        # 1. CONFIGURACIÓN DE PÁGINA
        # Usamos márgenes PEQUEÑOS (0.5 cm) para aprovechar al máximo la hoja
        margen = 0.5 * cm
        page_size = landscape(LEGAL)  # Ancho aprox: 35.5 cm

        doc = SimpleDocTemplate(
            filepath,
            pagesize=page_size,
            rightMargin=margen,
            leftMargin=margen,
            topMargin=margen,
            bottomMargin=margen,
        )

        elements = []
        styles = getSampleStyleSheet()

        # 2. ESTILOS DE FUENTE (Más pequeños para que quepa todo)
        estilo_titulo = ParagraphStyle(
            "TituloReporte",
            parent=styles["Heading1"],
            alignment=TA_CENTER,
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkblue,
        )

        # Bajamos fuente a 7pt para asegurar que quepan las columnas
        estilo_celda = ParagraphStyle(
            "CeldaTabla",
            parent=styles["Normal"],
            fontSize=7,
            leading=8,
            alignment=TA_LEFT,
            wordWrap="CJK",
        )
        estilo_header = ParagraphStyle(
            "HeaderTabla",
            parent=estilo_celda,
            fontSize=8,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            textColor=colors.whitesmoke,
        )

        elements.append(Paragraph(f"{titulo_reporte}", estilo_titulo))

        # 3. FILTRAR COLUMNA ID Y PREPARAR DATOS
        # Obtenemos todas las columnas MENOS 'id' (insensible a mayúsculas)
        todas_cols = list(datos[0].keys())
        columnas_visibles = [c for c in todas_cols if c.lower() != "id"]

        # Headers
        headers = [
            Paragraph(str(c).replace("_", " ").upper(), estilo_header)
            for c in columnas_visibles
        ]
        table_data = [headers]

        # Filas
        for fila in datos:
            row_data = []
            for col in columnas_visibles:
                val = fila.get(col, "")
                texto = str(val) if val is not None else ""
                row_data.append(Paragraph(texto, estilo_celda))
            table_data.append(row_data)

        # 4. CALCULAR ANCHOS NORMALIZADOS
        # Ancho útil = Ancho Hoja - Márgenes Izq/Der
        ancho_util = page_size[0] - (2 * margen)

        col_widths = calcular_anchos_proporcionales(
            datos, columnas_visibles, ancho_util
        )

        # 5. CREAR TABLA
        t = Table(table_data, colWidths=col_widths, repeatRows=1)

        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Centrado vertical
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.whitesmoke, colors.white],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),  # Padding reducido
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        elements.append(t)

        doc.build(elements)
        print(f"📄 PDF Generado: {filepath}")
        return f"/static/reports/{nombre_archivo}"

    except Exception as e:
        print(f"❌ Error CRÍTICO generando PDF:")
        traceback.print_exc()
        return None
