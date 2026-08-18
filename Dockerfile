FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf-2.0-0 \
    libffi8 shared-mime-info fonts-dejavu-core curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN chmod +x /app/deploy/scripts/entrypoint.sh
ENTRYPOINT ["/app/deploy/scripts/entrypoint.sh"]
CMD ["gunicorn", "funeraria.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
