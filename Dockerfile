# syntax=docker/dockerfile:1

# ---------- Stage 1: TypeScript build ----------
FROM node:20-slim AS ts-build

WORKDIR /build

COPY ts/package.json ts/package-lock.json ./
RUN npm ci

COPY ts ./ts
RUN npm run build

# Strip dev-only dependencies so only production deps remain
RUN npm prune --production

# ---------- Stage 2: Python + runtime ----------
FROM python:3.12-slim

# Create a non-root user for defense-in-depth
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Install Node.js 20.x (needed for the TypeScript CLI at runtime)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python package with server extras (FastAPI/uvicorn)
COPY --chown=app:app pyproject.toml README.md ./
COPY --chown=app:app vercel_templates ./vercel_templates
RUN pip install --no-cache-dir ".[server]" \
    && pip cache purge

# Copy compiled TypeScript artifacts and production node_modules from build stage
COPY --chown=app:app --from=ts-build /build/ts/dist ./ts/dist
COPY --chown=app:app --from=ts-build /build/ts/package.json ./ts/package.json
COPY --chown=app:app --from=ts-build /build/node_modules ./ts/node_modules

# Verify both entry points are present and executable
RUN vercel-templates --help > /dev/null \
    && node /app/ts/dist/cli.js --help > /dev/null

ENV PYTHONUNBUFFERED=1
USER app

CMD ["vercel-templates", "--help"]
