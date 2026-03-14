# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# Installiert alle Abhängigkeiten inkl. Build-Tools (gcc, etc.)
# Das Builder-Image landet NICHT im finalen Image → kleinere Angriffsfläche
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Build-Dependencies für psycopg2 und Kryptographie-Bibliotheken
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Zuerst nur pyproject.toml kopieren – Layer-Cache: pip install wird nur
# neu ausgeführt wenn sich die Dependencies geändert haben, nicht der App-Code
COPY pyproject.toml .

# pip install in separates Verzeichnis – wird im Runtime-Stage sauber kopiert
RUN pip install --no-cache-dir --prefix=/install .

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# Schlankes Image ohne Build-Tools, pip oder gcc
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# curl für Health Check – kein pip, keine Build-Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root User anlegen (uid 1000) – Principle of Least Privilege
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Installierte Packages aus Builder-Stage übernehmen
COPY --from=builder /install /usr/local

# App-Code kopieren
COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser tests/ ./tests/

# Uploads-Verzeichnis anlegen mit korrekten Berechtigungen
RUN mkdir -p /app/uploads && chown appuser:appuser /app/uploads

# Als non-root User ausführen
USER appuser

EXPOSE 8000

# Health Check: FastAPI /health Endpoint
# start_period gibt dem Server Zeit zum Hochfahren vor dem ersten Check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD curl -f http://localhost:8000/health || exit 1

# 2 Worker für Standard-VPS – bei mehr CPUs via ENV WORKERS überschreiben
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
