FROM python:3.12-slim

# System-Tools für Audio und Installation
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

# Poetry installieren
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Das gesamte Verzeichnis kopieren
COPY . .

# Abhängigkeiten via Poetry installieren
RUN poetry install

ENV LD_LIBRARY_PATH=/app/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib:/app/.venv/lib/python3.12/site-packages/nvidia/cublas/lib

# Port für Streamlit
EXPOSE 8501

# Startbefehl via poetry run
ENTRYPOINT ["poetry", "run", "streamlit", "run", "src/nlp_assistant/frontend/frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]