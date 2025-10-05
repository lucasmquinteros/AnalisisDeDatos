# Imagen base de Python
FROM python:3.12-slim

# Evita preguntas interactivas en la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements (si los tenés, si no podés instalar directo)
COPY requirements.txt .

# Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto para Jupyter
EXPOSE 8888

# Comando por defecto: iniciar Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
