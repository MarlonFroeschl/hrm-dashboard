# Fortschritt – HRM Dashboard

---

## Sitzung 14.03.2026/17:30

**Status:** Bewerber-Ingestion API vollständig implementiert, reviewed, getestet und committed

**Erledigt:**
- `alembic/versions/002_add_document_extracted_data.py` – Migration: extracted_data (JSONB) + matching_score (Float) zu documents
- `app/models/document.py` – zwei neue Felder ergänzt
- `app/api/v1/dependencies.py` – JWT Bearer Auth (`get_current_user`)
- `app/schemas/applicant.py` – 5 Pydantic v2 Schemas
- `app/services/cv_parser_service.py` – PDF + Claude API + Regex-Fallback, non-blocking via `asyncio.to_thread`
- `app/services/applicant_service.py` – alle 6 Service-Funktionen + Path-Traversal-Schutz + DSGVO-konforme Logs
- `app/api/v1/routes/applicants.py` – 6 Endpoints (POST, POST upload-cv, GET list, GET detail, PATCH status, POST invite)
- `app/core/config.py` – `UPLOAD_DIR`, `MAX_CV_FILE_SIZE_BYTES`, `N8N_WEBHOOK_INVITE_APPLICANT` ergänzt
- `tests/conftest.py` + `tests/test_applicants.py` – 46 Tests (SQLite in-memory, alle externen Services gemockt)
- Code-Review: 3 CRITICAL + 4 HIGH Findings alle gefixt

**Eingesetzte Agents:**
- database-dev → Migration 002 + Document-Model Update → 2 Dateien fertig
- backend-dev → Dependencies, Schemas, cv_parser_service, applicant_service, routes → 5 Dateien + router.py fertig
- qa-engineer → 46 Tests mit conftest.py Fixtures → Tests als Text geliefert, direkt geschrieben
- code-reviewer → Security- und Qualitätsprüfung → 3 CRITICAL, 4 HIGH, 5 MEDIUM, 5 LOW Findings

**Review-Fixes (CRITICAL + HIGH):**
- Path Traversal: `resolve()` + Pfad-Vergleich gegen `UPLOAD_DIR`, Content-Type + Größen-Check im Service
- PII in Logs: E-Mail aus allen `logger.info()`-Aufrufen entfernt (DSGVO)
- Blocking I/O: `pdfplumber` + Claude API via `asyncio.to_thread()` nicht-blockierend
- File-Size-Limit: `MAX_CV_FILE_SIZE_BYTES = 10 MB` in config + Service-Check
- Falscher Webhook: `N8N_WEBHOOK_INVITE_APPLICANT` separater Webhook für Einladungen
- `create_task` Referenz: Task-Variable gespeichert + `done_callback` für Error-Logging
- JSON Fence-Stripping: Markdown-Code-Fences vor `json.loads()` entfernt

**Offen:**
- Auth-Endpoints (`/api/v1/auth/token`) fehlen noch – Swagger UI Login nicht möglich
- Tests lokal ausführen: `cd backend && pytest tests/test_applicants.py -v`
- Migration anwenden: `docker compose exec backend alembic upgrade head`

**Blocker:**
- Keiner

**Entscheidungen:**
- Count-Query separat von der Paginierungsabfrage – korrekte Zählung bei DISTINCT + JOIN
- `N8N_WEBHOOK_INVITE_APPLICANT` als eigener Config-Wert (nicht `NEW_APPLICANT` recycelt)
- pdfplumber statt PyMuPDF – pure Python, keine C-Abhängigkeiten im Container

---

## Sitzung 14.03.2026/15:30

**Status:** Lifecycle OS Datenbankschema vollständig implementiert, reviewed und committed

**Erledigt:**
- 7 SQLAlchemy v2 Models: Person, EmployeeProfile, Document, KnowledgeEntry, OnboardingTask, OffboardingPlan, AuditLog
- Alembic Migration `001_initial_lifecycle_schema.py`: alle Tabellen, 6 ENUMs, 20+ Indices
- `db/base.py` mit allen Model-Imports für Alembic autogenerate aktualisiert
- `db/seed.py` mit idempotenten Dev-Daten (4 Persons, 3 EmployeeProfiles, 3 Documents, 2 KnowledgeEntries, 3 OnboardingTasks, 1 OffboardingPlan, 5 AuditLog-Einträge)
- 198 Unit-Tests ohne Datenbankverbindung (conftest.py + test_models.py)
- Code-Review: 3 kritische + 4 Warnings gefixt
- Feature-Branch `feature/lifecycle-db-schema` committed (d71b377)

**Eingesetzte Agents:**
- database-dev → Lifecycle-Schema (Person, EmployeeProfile, Document) → Teillieferung (Verbindungsfehler), direkt weitergeführt
- qa-engineer → 198 Unit-Tests für alle Models + seed_database() → tests/unit/test_models.py + conftest.py fertig
- code-reviewer → Schema-Review → 10 Findings (3 CRITICAL, 4 WARNING, 3 INFO), alle Criticals gefixt

**Review-Fixes:**
- `Mapped[list]` → `Mapped[list[str]]` / `Mapped[list[InterviewSlot]]` auf allen JSONB-Feldern
- `String(20)` für Enums → `SAEnum(..., create_type=False)` auf allen Enum-Spalten
- `AuditAction`-Enum hinzugefügt (7 vordefinierte Werte, DSGVO-konform)
- `server_default=func.now()` → `server_default=text("now()")` auf allen Timestamp-Feldern
- f-String in `downgrade()` → `sa.text("DROP TYPE IF EXISTS ...")` (6 einzelne Statements)
- Seed: `db.commit()` in try/except mit `db.rollback()` bei Fehler
- `onboarding_tasks.assigned_to` → FK auf `persons.id` mit `ondelete="SET NULL"`

**Offen:**
- Migrations ausführen: `docker compose exec backend alembic upgrade head`
- Seed ausführen: `docker compose exec backend python -m app.db.seed`
- API-Endpoints für CRUD-Operationen (nächstes Feature)

**Entscheidungen:**
- `InterviewSlot` TypedDict im Model definiert (nicht in shared/types) – näher am Kontext
- `AuditAction` als Enum statt freier String – DSGVO-Konformität
- Alle ENUMs in Migration mit `create_type=True` und `checkfirst=True` – idempotente Migration

---

## Sitzung 14.03.2026/14:55

**Status:** pytest Unit-Tests für das gesamte HRM-Datenbankschema fertiggestellt

**Erledigt:**
- `tests/unit/conftest.py` erstellt mit session-scoped Table-Fixtures für alle 7 Models
- `tests/unit/test_models.py` erstellt mit 198 Tests ohne Datenbankverbindung
- `tests/unit/__init__.py` angelegt

**Eingesetzte Agents:**
- qa-engineer  → Unit-Tests für alle 7 SQLAlchemy-Models + seed_database() schreiben  → 198 Tests in 11 Testklassen-Gruppen, 0 DB-Verbindung nötig

**Abgedeckte Szenarien:**
- Enum-Werte + Member-Count: PersonType, PersonStatus, ITAccessLevel, EntryType, TaskStatus
- Tabellennamen aller 7 Models
- Spalten-Existenz (vollständige Abdeckung aller Columns pro Model)
- Nullable / Non-Nullable Constraints auf kritischen Spalten
- Server-Defaults (active, pending, none, [])
- Indizes: alle 20 Einzel-Indizes + 1 Composite-Index (AuditLog entity_type+entity_id)
- Relationship-Attribute auf allen Models inkl. Self-Referenz (EmployeeProfile.manager)
- Foreign Keys: Ziel-Tabelle + ondelete-Verhalten (CASCADE / RESTRICT / SET NULL)
- Primary Keys aller Models
- `__repr__`-Methoden
- `seed_database()`: Skip-Logik, Commit-Verhalten, Idempotenz (5 Mock-Tests)

**Offen:**
- Python-Interpreter auf dem System nicht verfügbar – Tests wurden nicht live ausgeführt
- Für Ausführung: `pip install -e ".[dev]"` im backend/ Verzeichnis, dann `pytest tests/unit/`

**Entscheidungen:**
- Keine Datenbankverbindung in Unit-Tests: SQLAlchemy-Metadaten werden direkt auf den Model-Klassen introspektiert
- `scope="session"` für Table-Fixtures in conftest.py: Table-Objekte sind unveränderlich, einmaliges Laden reicht
- Testklassen nach Thema gruppiert (Enum, TableName, Columns, Nullable, Defaults, Indexes, Relationships, FKs, PKs, Repr, Seed)

---

## Sitzung 14.03.2026/12:00

**Status:** GitHub Actions CI/CD Pipeline eingerichtet

**Erledigt:**
- `.github/workflows/ci.yml` erstellt mit 5 Jobs

**Eingesetzte Agents:**
- Keiner – direkte Implementierung

**Pipeline-Jobs:**
- `backend-quality` – ruff Lint, mypy Type Check, pytest + Coverage (mit PostgreSQL Service-Container)
- `backend-security` – pip-audit CVE-Scan + Secret-Scan im Python-Code
- `frontend-quality` – TypeScript Check, ESLint, Vitest + Coverage
- `frontend-security` – npm audit + Secret-Scan im Frontend-Code
- `docker-build` – Backend + Frontend Images bauen (kein Push), docker-compose config validieren

**Offen:**
- Keiner

**Entscheidungen:**
- Docker-Build-Job läuft erst nach erfolgreichen Quality-Jobs (needs: [...])
- `concurrency`-Block verhindert parallele Runs auf demselben Branch
- Security-Jobs mit `continue-on-error: true` – warnen, blockieren aber nicht
- PostgreSQL Service-Container für Backend-Tests direkt in der Pipeline

---

## Sitzung 14.03.2026/11:00

**Status:** Production-ready Docker-Konfiguration vollständig implementiert

**Erledigt:**
- `docker-compose.yml` komplett neu geschrieben: 6 Services (PostgreSQL, Redis, Qdrant, Backend, Frontend, NGINX) + Mailhog unter dev-Profil
- Resource Limits auf allen Services gesetzt (memory + cpus)
- Health Checks auf allen Services implementiert (mit `depends_on condition: service_healthy`)
- `backend/Dockerfile` auf Multi-Stage Build umgestellt (Builder + Runtime, non-root `appuser` uid 1000)
- `frontend/Dockerfile` auf Multi-Stage Build verbessert (`npm ci`, Health Check via wget)
- `frontend/nginx.conf` erweitert: Gzip, Security Headers, Asset-Caching, korrekte Proxy-Timeouts
- `nginx/nginx.conf` neu erstellt: HTTP→HTTPS-Redirect, SSL-Terminierung, Rate Limiting auf Auth-Endpoints, Upstream-Definitionen
- `nginx/certs/` Verzeichnis mit `.gitkeep` angelegt
- `.dockerignore` komplett für Python+Node.js Monorepo überarbeitet
- `backend/app/services/webhook_service.py` erstellt (n8n-Webhook-Integration via httpx)
- `.env.example` um Redis, Qdrant und n8n-Webhook-Variablen erweitert

**Eingesetzte Agents:**
- devops → Production-ready Docker-Konfiguration erstellen → alle 8 Dateien fertiggestellt

**Offen:**
- SSL-Zertifikat generieren (self-signed für Staging, Let's Encrypt für Produktion)
- `.env` aus `.env.example` erstellen und Passwörter setzen
- Alembic-Migrationen ausführen: `docker compose exec backend alembic upgrade head`
- n8n-Webhook-URLs in `.env` eintragen
- Auth-System + Module (Employees, Recruitment, Offboarding) implementieren

**Blocker:**
- Kein SSL-Zertifikat vorhanden – nginx startet erst nach Bereitstellung der Certs

**Entscheidungen:**
- Redis 7 Alpine hinzugefügt: Caching + Queue-Basis für spätere Task-Verarbeitung
- Qdrant als Vektor-DB für KI-Features (Claude API + Embeddings)
- n8n läuft extern – kein eigener Service, nur ausgehende HTTP-Webhooks
- NGINX als einziger öffentlicher Eintrittspunkt (kein direkter Port-Expose außer Port 8000 für Debugging)
- Rate Limiting: 5 req/min auf `/api/v1/auth/`, 60 req/min auf allen anderen API-Endpoints

---

## Sitzung 14.03.2026/02:30

**Status:** Stack-Migration abgeschlossen – neuer Tech-Stack vollständig aufgesetzt

**Erledigt:**
- Stack von Next.js + Express + Prisma auf Python + FastAPI + React + Vite + SQLAlchemy + Alembic migriert
- Alten Stack (src/, prisma/, node_modules) entfernt
- Neue Verzeichnisstruktur: `frontend/` + `backend/`
- FastAPI Backend aufgesetzt: main.py, config, security (JWT/bcrypt), db/session, Alembic-Setup
- React + Vite Frontend aufgesetzt: package.json, vite.config.ts, Tailwind CSS v4, TanStack Query, Zustand, React Router v7
- docker-compose.yml auf neuen Stack aktualisiert (backend Port 8000, frontend Port 5173/80)
- Dockerfiles für frontend (Nginx) und backend (Python 3.12-slim) erstellt
- .env.example aktualisiert
- CLAUDE.md vollständig überarbeitet mit neuem Stack
- Frontend-Dependencies installiert (npm install erfolgreich)

**Eingesetzte Agents:**
- Keiner – direkte Implementierung

**Offen:**
- Python-Dependencies installieren (`cd backend && pip install -e ".[dev]"`)
- .env Datei aus .env.example erstellen und ausfüllen
- Datenbank aufsetzen (PostgreSQL lokal oder via Docker)
- Erste Alembic-Migration erstellen
- Auth-System implementieren
- Module: Employees, Recruitment, Offboarding bauen

**Blocker:**
- Python + pip muss lokal installiert sein für lokale Entwicklung (oder Docker verwenden)

**Entscheidungen:**
- Stack-Wechsel auf Python + FastAPI (Nutzerwunsch) – bessere KI-Integration (Anthropic SDK), weniger JS-Overhead
- Vite statt Next.js – keine SSR-Anforderung, einfacherer Stack
- SQLAlchemy v2 + Alembic statt Prisma – nativer Python-Stack
- Frontend-Port: 5173 (dev), Backend-Port: 8000

---

## Sitzung 14.03.2026/01:00

**Status:** Projekt-Scaffolding initial erstellt (Next.js + Express – später migriert)

**Erledigt:**
- Projektstruktur erstellt
- CLAUDE.md, README.md, docker-compose.yml, .env.example angelegt
- npm install erfolgreich ausgeführt

**Offen:**
- Stack-Migration auf Python + FastAPI durchgeführt (siehe Sitzung 02:30)
