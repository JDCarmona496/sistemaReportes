import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os

# Nombre de la carpeta de logs
LOG_DIR = "logs"

def configure_logging():
    # 1. Crear carpeta de logs si no existe
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 2. Configurar el formato (Fecha - Nivel - Mensaje)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # 3. Handler de Consola (Para ver en pantalla mientras desarrollas)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 4. Handler de Archivo (Rotativo diario)
    # Crea un archivo nuevo cada medianoche y guarda historial de 30 días
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        when="midnight",
        interval=1,
        backupCount=30, # Guardar logs de un mes
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d" # El archivo viejo se llamará app.log.2026-01-21

    # 5. Aplicar configuración al Logger Raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Capturar INFO, WARNING, ERROR, CRITICAL
    
    # Evitar duplicar handlers si se recarga la app
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    # Silenciar un poco los logs ruidosos de librerías externas
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    print("✅ Sistema de Logging Iniciado. Los registros se guardarán en /logs")