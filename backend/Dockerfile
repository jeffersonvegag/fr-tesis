FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    libpq-dev \
    gcc \
    libboost-all-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar todo el código fuente
COPY . .

# Instalar pip y actualizarlo
RUN pip install --no-cache-dir --upgrade pip

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Asegurarse de que Python pueda encontrar los módulos
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Comando de inicio del servidor
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
