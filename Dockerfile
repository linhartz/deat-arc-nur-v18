# Base image
FROM python:3.11-slim

# Nastavení pracovního adresáře
WORKDIR /app

# Zkopíruj vše do kontejneru
COPY . /app

# Instalace Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Railway používá dynamický port přes proměnnou PORT
EXPOSE 8000

# Start serveru s podporou dynamického portu
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
