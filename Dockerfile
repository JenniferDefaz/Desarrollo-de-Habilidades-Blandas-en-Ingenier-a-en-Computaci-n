FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evitar que Python bufferice la salida estándar (útil para logs)
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . /app/

# --- Seguridad: crear usuario no-root para ejecutar la app (WARN 4.1) ---
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser \
    && chown -R appuser:appgroup /app

USER appuser

# --- Healthcheck (WARN 4.6 / 5.27) ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/login/')" || exit 1

EXPOSE 8000
