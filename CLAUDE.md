# HRM Dashboard

## Beschreibung
Vollautomatisches HR-Management-Dashboard mit KI-Unterstützung und Schnittstellen für den gesamten Mitarbeiter-Lebenszyklus – vom Bewerbungsprozess bis zum Ausscheiden aus dem Unternehmen.

## Tech-Stack
- **Frontend:** React 19 + TypeScript, Vite, Tailwind CSS v4, React Router v7, TanStack Query v5, Zustand
- **Backend:** Python 3.12 + FastAPI, Uvicorn (2 Worker)
- **Datenbank:** PostgreSQL 16 mit SQLAlchemy v2 + Alembic
- **Cache / Queues:** Redis 7 Alpine (AOF-Persistenz, LRU-Eviction)
- **Vektor-DB:** Qdrant (KI-Embeddings, Port 6333 HTTP / 6334 gRPC)
- **Auth:** JWT (Access Token 15min + Refresh Token 7d) via python-jose + passlib/bcrypt
- **KI-Integration:** Claude API (Anthropic) – Kandidatenanalyse, Onboarding-Assistent, Offboarding-Checklisten
- **Automatisierung:** n8n (extern, kein eigener Service) – Backend kommuniziert via ausgehende HTTP-Webhooks
- **Testing:** Vitest + Testing Library (Frontend), pytest + httpx (Backend), Playwright (E2E)
- **Container:** Docker + Docker Compose, NGINX als Reverse Proxy (SSL-Terminierung)

## Projektstruktur
```
frontend/                    # React + Vite App (Port 5173 dev / 80 prod)
├── src/
│   ├── components/
│   │   ├── ui/              # Basis-Komponenten (Button, Input, Modal, ...)
│   │   ├── layout/          # Sidebar, Header, Navigation
│   │   ├── forms/           # Formulare
│   │   └── charts/          # KPI-Charts
│   ├── pages/               # Route-Seiten
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── employees/
│   │   ├── recruitment/
│   │   └── offboarding/
│   ├── hooks/               # Custom React Hooks
│   ├── stores/              # Zustand Stores
│   ├── utils/               # API-Client, Helpers
│   └── types/               # TypeScript Typen
backend/                     # FastAPI App (Port 8000)
├── app/
│   ├── api/v1/routes/       # Route Handler
│   ├── core/                # config.py, security.py
│   ├── db/                  # session.py, base.py
│   ├── models/              # SQLAlchemy Models
│   ├── schemas/             # Pydantic Schemas (Request/Response DTOs)
│   ├── services/            # Business Logic
│   └── main.py              # FastAPI App Entry Point
├── alembic/                 # DB-Migrationen
└── tests/
```

## Commands

### Frontend
```bash
cd frontend
npm install       # Dependencies installieren
npm run dev       # Dev-Server starten (http://localhost:5173)
npm run build     # Produktions-Build
npm run test      # Vitest Tests
npm run lint      # ESLint
```

### Backend
```bash
cd backend
pip install -e ".[dev]"           # Dependencies + Dev-Tools installieren
uvicorn app.main:app --reload     # Dev-Server starten (http://localhost:8000)
pytest                            # Tests ausführen
ruff check .                      # Linting
alembic upgrade head              # Migrationen anwenden
alembic revision --autogenerate -m "description"  # Neue Migration erstellen
```

### Docker
```bash
cp .env.example .env       # .env anlegen und ausfüllen
docker compose up -d       # Stack starten
docker compose up -d --build  # Stack neu bauen
docker compose --profile dev up -d  # Mit Mailhog
```

## API-Dokumentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

## Mitarbeiter-Lebenszyklus Module
1. **Recruitment** – Stellenausschreibungen, Bewerbungseingang, KI-Screening, Interview-Scheduling
2. **Onboarding** – Checklisten, Dokumentenupload, Willkommens-E-Mail, IT-Zugang
3. **Employee Management** – Stammdaten, Organigramm, Abwesenheiten, Leistungsbeurteilungen
4. **Offboarding** – Austrittsinterview, Zugangsentzug, Zeugnis-Generierung, Alumni-Status

## Konventionen

### Frontend
- Komponenten: PascalCase, eine Komponente pro Datei
- Funktionen/Variablen: camelCase
- Typen: PascalCase (kein "I"-Prefix)
- API-Calls: über `src/utils/api.ts` mit axios-Instance
- Dateien: kebab-case für Utilities, PascalCase für Komponenten

### Backend
- Route Handler: klein, delegieren direkt an Services
- Services: Business Logic, keine SQLAlchemy-Queries direkt (via Repository-Pattern)
- Schemas: Pydantic v2, separate Request/Response Schemas
- Models: SQLAlchemy v2 Mapped-Columns Syntax
- Migrations: immer via Alembic, niemals manuell

## Rollen (RBAC)
- `ADMIN` – Vollzugriff
- `HR_MANAGER` – Alle HR-Funktionen
- `RECRUITER` – Nur Recruitment-Modul
- `MANAGER` – Eigenes Team, Beurteilungen
- `EMPLOYEE` – Nur eigene Daten

## Sicherheit
- DSGVO-konform: Datenspeicherung in EU, Löschkonzept für Bewerber (nach 6 Monaten)
- Rate Limiting auf Auth-Endpoints
- Input Validation mit Pydantic v2 an jedem Endpoint
- CORS nur für konfigurierte Origins
- Passwörter mit bcrypt (12 rounds)

## Erwartete Last
- ~100–500 gleichzeitige User im Normalbetrieb
- ~1000 bei Spitzen
- Datenbank: ~10.000 Mitarbeiterdatensätze, ~50.000 Bewerbungen

## Deployment

### Ports
| Service    | Port intern | Port extern       | Zugang           |
|------------|-------------|-------------------|------------------|
| NGINX      | 80/443      | 80/443            | Öffentlich       |
| Backend    | 8000        | 8000 (Debugging)  | Direkt + via NGINX |
| Frontend   | 80          | –                 | Nur via NGINX    |
| PostgreSQL | 5432        | –                 | Nur intern       |
| Redis      | 6379        | –                 | Nur intern       |
| Qdrant     | 6333/6334   | –                 | Nur intern       |
| Mailhog    | 1025/8025   | 1025/8025         | Nur dev-Profil   |

### Startup-Reihenfolge
`postgres` → `redis` → `qdrant` → `backend` → `frontend` → `nginx`

### Wichtige Commands
```bash
cp .env.example .env                          # .env anlegen
docker compose up -d                          # Stack starten
docker compose up -d --build                  # Neu bauen
docker compose --profile dev up -d            # Mit Mailhog
docker compose exec backend alembic upgrade head  # Migrationen
docker compose logs -f backend                # Backend-Logs
docker compose ps                             # Status + Health
```

### SSL-Zertifikat (self-signed für Staging)
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./nginx/certs/server.key \
  -out ./nginx/certs/server.crt \
  -subj "/CN=localhost"
```

### n8n Integration
n8n läuft extern – kein eigener Service. Das Backend sendet Webhooks via `webhook_service.py`:
- `N8N_WEBHOOK_NEW_APPLICANT` – neuer Bewerber eingegangen
- `N8N_WEBHOOK_ONBOARDING_START` – Onboarding gestartet
- `N8N_WEBHOOK_OFFBOARDING_START` – Offboarding eingeleitet
- `N8N_WEBHOOK_EMPLOYEE_UPDATED` – Mitarbeiterdaten geändert

Leere URLs werden still ignoriert (kein Fehler).

## Offene Entscheidungen
- [ ] E-Mail-Provider: SMTP Self-hosted (Mailhog lokal) vs. externes Relay
- [ ] Dateiupload-Storage: Lokal vs. MinIO (S3-kompatibel, Self-hosted)
- [ ] Background Jobs: Celery + Redis für async KI-Verarbeitung (Redis bereits vorhanden)
- [ ] SSL: self-signed (Staging) vs. Let's Encrypt (Produktion)
- [ ] Mehrsprachigkeit (i18n): DE/EN – noch nicht entschieden
