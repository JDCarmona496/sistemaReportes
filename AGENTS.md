# AGENTS.md — Sistema de Reportes BIOLAB

## Setup

- Python 3.14 virtual env at `backend/venv/`. Activate before running anything.
- `pip install -r backend/requirements.txt`
- PostgreSQL 18 required (DB: `reportes_db` on `localhost:5432`).
- PostgreSQL está instalado en `D:\Program Files\PostgreSQL\18\`. Si hay que cambiar la contraseña, editar temporalmente `pg_hba.conf` a `trust`, reiniciar el servicio, ejecutar `ALTER USER postgres WITH PASSWORD '12345';`, restaurar `pg_hba.conf` y reiniciar.
- Redis corre en una máquina virtual de Windows separada (accesible en `localhost:6379`). Iniciarla antes de levantar Celery o la app.
- LIS databases (`192.168.61.27`, `172.26.62.3`) require VPN access. Only test locally if connected.

## Run (from `backend/`)

Three processes needed for full functionality:

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
celery -A app.core.celery_app worker --loglevel=info --pool=solo
celery -A app.core.celery_app beat --loglevel=info
```

## Database and migrations

- **SQLAlchemy <2.0** only (pinned in requirements.txt). The codebase uses `declarative_base()`, `Column()`, and `session.query()` patterns. Do not introduce SQLAlchemy 2.0 API.
- **Alembic `env.py` is broken** — it contains a copy of `worker.py` instead of the Alembic environment config. `alembic upgrade head` may fail. Tables (`users`, `reports`, `system_settings`, celery tables) may have been created via `Base.metadata.create_all()`. The `users` table has no corresponding migration.
- Seed scripts (run sequentially from `backend/`):
  1. `python crear_admin.py` — creates admin@example.com / admin
  2. `python sembrar_config.py` — seeds `system_settings` table
  3. `python sembrar_scheduler.py` — seeds periodic Celery Beat tasks

## Architecture notes

- Monolithic backend at `backend/`. No workspace or multi-package layout.
- Frontend is vanilla JS ES modules served as static files from `backend/static/`.
- No bundler, no build step. CDN imports for Tailwind, Chart.js, SweetAlert2, Font Awesome.
- API routes: `/api/v1/...` (FastAPI), aggregated at `app/api/v1/api.py`.
- Auth: JWT via `/api/v1/login/access-token` (python-jose + bcrypt).

## What does NOT exist

- **No test framework, no linter, no type checker.** Don't run `pytest`, `ruff`, `mypy`, etc.
- **No CI/CD**, no Docker, no pre-commit hooks.
- **No `opencode.json`** or workspace config.
- Heavy use of `# type: ignore` comments is intentional and expected — SQLAlchemy 1.x with Pylance/Pyright produces many false positives.

## Git-ignored files

- `backend/.env` — credentials, DB URLs, LIS configs. Never commit.
- `backend/sembrar_reporte.py`, `backend/test_lis_connection.py` — excluded because they contain hardcoded credentials.
