# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# Node.js 22 LTS Alpine – baut den React/Vite-Bundle
# npm ci statt npm install: reproduzierbar, schneller, für CI geeignet
# ──────────────────────────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Zuerst nur package.json + package-lock.json kopieren
# Layer-Cache: npm ci wird nur neu ausgeführt wenn sich Dependencies geändert haben
COPY package.json package-lock.json ./

# npm ci: saubere Installation aus lock file, keine Überraschungen
RUN npm ci --frozen-lockfile

# App-Code kopieren und bauen
COPY . .

RUN npm run build

# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# nginx:alpine – nur statische Dateien servieren, kein Node.js im Produktions-Image
# Pinned auf 1.27-alpine für Reproduzierbarkeit
# ──────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Nginx-eigener User hat uid/gid 101 in nginx:alpine
# Wir nutzen den vorhandenen nginx-User, kein eigener nötig

# Vite-Build-Output in nginx document root
COPY --from=builder /app/dist /usr/share/nginx/html

# Eigene nginx-Konfiguration für SPA + API-Proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# nginx läuft auf Port 80, Worker-Process läuft als nginx-User (non-root)
# Der Master-Process benötigt root für Port-Binding – das ist Standard-Verhalten
EXPOSE 80

# Health Check via wget (busybox – in alpine vorhanden, kein curl nötig)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD wget -qO- http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
