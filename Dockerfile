FROM python:3.11-slim

# System-Abhängigkeiten installieren (OpenSCAD)
RUN apt-get update && \
    apt-get install -y openscad && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# Python-Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den restlichen Code in den Container kopieren
COPY . .

# Gunicorn verwenden, um die Flask-App produktionsreif zu starten
# Timeout auf 120 Sekunden, Worker auf 1 reduzieren, um RAM-Abstürze (OOM) zu verhindern!
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1", "main:app"]