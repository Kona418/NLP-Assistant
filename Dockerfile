FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH="/app/src"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root

RUN python -m spacy download de_core_news_sm && \
    python -m spacy download de_core_news_lg

COPY . /app

RUN mkdir -p src/nlp_assistant/data/audio

EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start the application
ENTRYPOINT ["streamlit", "run", "src/nlp_assistant/frontend/frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]