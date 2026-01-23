cat << 'EOF' > README_TECNICO.md
# 📘 Documentación Técnica: Sistema de Reportes BIOLAB
**Versión:** 1.0 (Entorno Desarrollo Local)
**Tecnologías:** FastAPI (Python), Redis (WSL2), Uvicorn.
**Fecha:** Enero 2026

---

## 1. Infraestructura: Servidor Redis (WSL2)

### 1.1 Instalación
Comandos ejecutados en la terminal Ubuntu (WSL):
```bash
sudo apt-get update
sudo apt-get install redis-server

# Iniciar servicio
sudo service redis-server start

# Reiniciar (Obligatorio tras cambios de config)
sudo service redis-server restart

# Verificar estado
sudo service redis-server status

# Monitor en tiempo real (Sniffer)
redis-cli monitor