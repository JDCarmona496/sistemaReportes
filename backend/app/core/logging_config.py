import os
import logging
from logging.handlers import RotatingFileHandler # Usaremos este o FileHandler simple

def configure_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Archivo de log principal
    log_file = os.path.join(log_dir, "app.log")

    # --- CAMBIO AQUÍ ---
    # En lugar de TimedRotatingFileHandler (que rompe en Windows por fechas)
    # Usamos RotatingFileHandler basado en tamaño (ej: 10MB) que es más seguro
    # O simplemente FileHandler.
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    
    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Configuración básica
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(), # Salida por consola
            file_handler             # Salida a archivo (Seguro para Windows)
        ]
    )
    
    # Reducir ruido de librerías externas
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    
    print(f"✅ Sistema de Logging Iniciado. (Modo Seguro Windows)")