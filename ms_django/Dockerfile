# Imagen ligera de Python
FROM python:3.10-slim

# Configuraciones para evitar archivos .pyc y ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias para PostgreSQL (psycopg2) y el compilador gcc
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalamos las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . .

# Puerto por defecto de Django en tu proyecto
EXPOSE 8001

# Comando para iniciar Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]