FROM python:3.10-slim

WORKDIR /app

# Instalamos dependencias de Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de auditoría
COPY app.py .

# Puerto de Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]