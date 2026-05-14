FROM python:3.10-slim

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la lógica del IVA
COPY main.py .

# Puerto de FastAPI
EXPOSE 8050

# Comando para iniciar con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]