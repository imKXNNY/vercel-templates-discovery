# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install system dependencies: Node.js + npm for the TypeScript CLI, plus build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python package files
COPY pyproject.toml README.md ./
COPY vercel_templates ./vercel_templates

# Install the Python package
RUN pip install --no-cache-dir .

# Copy and build the TypeScript implementation
COPY ts/package.json ts/package-lock.json ./ts/
RUN cd ts && npm ci

COPY ts ./ts
RUN cd ts && npm run build

# Default command shows help; both CLIs are available in PATH
ENV PYTHONUNBUFFERED=1

CMD ["vercel-templates", "--help"]
