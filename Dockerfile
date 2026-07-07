FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VTD_DB_PATH=/data/templates.db

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY vercel_templates/ ./vercel_templates/

RUN pip install --no-cache-dir -e ".[server,semantic]"

VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["vercel-templates"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
