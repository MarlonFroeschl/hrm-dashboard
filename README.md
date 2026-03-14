# HRM Dashboard

Vollautomatisches HR-Management-Dashboard mit KI-Unterstützung für den gesamten Mitarbeiter-Lebenszyklus – vom Bewerbungsprozess bis zum Ausscheiden aus dem Unternehmen.

## Voraussetzungen

- Node.js >= 20.0.0
- npm >= 10.0.0
- Docker + Docker Compose

## Setup

```bash
# 1. Repository klonen
git clone <repo-url>
cd hrm-dashboard

# 2. Environment-Variablen anlegen
cp .env.example .env
# .env anpassen (DB-Credentials, JWT-Secrets, API-Keys)

# 3. Dependencies installieren
npm install

# 4. Datenbank starten (via Docker)
docker compose up -d postgres

# 5. Datenbankschema erstellen
npx prisma migrate dev --name init

# 6. Dev-Server starten (Frontend + Backend)
npm run dev
```

Frontend läuft auf: http://localhost:3000
Backend API läuft auf: http://localhost:4000
Prisma Studio: `npx prisma studio`

## Mit Docker (vollständig)

```bash
cp .env.example .env
# .env anpassen
docker compose up -d --build
```

## Verfügbare Scripts

| Command | Beschreibung |
|---|---|
| `npm run dev` | Frontend + Backend parallel starten |
| `npm run build` | Produktions-Build |
| `npm run test` | Alle Tests ausführen |
| `npm run lint` | ESLint |
| `npx prisma migrate dev` | Migration erstellen + anwenden |
| `npx prisma studio` | Datenbank-GUI |
| `docker compose up -d` | Stack starten |
| `docker compose logs -f` | Logs verfolgen |

## Projektstruktur

```
hrm-dashboard/
├── src/
│   ├── client/        # Next.js 15 Frontend (Port 3000)
│   ├── server/        # Express API (Port 4000)
│   └── shared/        # Geteilte TypeScript-Typen
├── tests/             # Unit, Integration, E2E Tests
├── prisma/            # Datenbankschema + Migrationen
├── docs/              # Dokumentation
└── scripts/           # Build/Deploy-Skripte
```

## Module

- **Recruitment** – Stellenausschreibungen, Bewerbermanagement, KI-Screening
- **Onboarding** – Checklisten, Dokumentenverwaltung
- **Employee Management** – Stammdaten, Organigramm, Abwesenheiten
- **Offboarding** – Austrittsprozess, Zeugnis-Generierung

## Lizenz

Proprietär – Nexurve-Systems GmbH
