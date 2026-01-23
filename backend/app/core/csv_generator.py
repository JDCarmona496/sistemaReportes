import csv
import os
import re  # <--- IMPORTANTE PARA LIMPIAR EL NOMBRE


def crear_csv_generico(datos: list, titulo_reporte: str, usuario_id: int):
    """
    Genera un archivo CSV a partir de una lista de diccionarios.
    """
    if not datos:
        return None

    # 1. Rutas
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)

    # 2. LIMPIEZA DE NOMBRE (Sanitización)
    # Reemplazamos espacios por guiones bajos
    nombre_limpio = titulo_reporte.replace(" ", "_")
    # Quitamos caracteres prohibidos en Windows/Linux (incluyendo el / asesino)
    nombre_limpio = re.sub(r'[\\/*?:"<>|]', "", nombre_limpio)

    nombre_archivo = f"Reporte_{usuario_id}_{nombre_limpio}.csv"
    filepath = os.path.join(output_dir, nombre_archivo)

    # 3. Detectar columnas (Keys del primer diccionario)
    columnas = list(datos[0].keys())

    # 4. Escribir CSV
    try:
        # 'utf-8-sig' ayuda a que Excel abra bien las tildes y ñ
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columnas, delimiter=";")
            writer.writeheader()
            writer.writerows(datos)

        print(f"📄 CSV Generado en: {filepath}")
        return f"/static/reports/{nombre_archivo}"

    except Exception as e:
        print(f"❌ Error escribiendo CSV: {e}")
        return None
