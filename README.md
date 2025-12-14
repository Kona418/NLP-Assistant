# NLP Assistant

Ein intelligenter Sprachassistent mit Spracherkennung, Natural Language Processing und Home Assistant Integration.

## Features

- **Spracherkennung**: Konvertierung von Sprache zu Text mit Faster-Whisper
- **Intent Recognition**: Automatische Erkennung von Nutzerabsichten mit Machine Learning (scikit-learn)
- **Text-to-Speech**: Deutsche Sprachausgabe mit Piper TTS (mehrere Stimmen)
- **Home Assistant Integration**: Nahtlose Steuerung von Smart-Home-Geräten über REST API
- **Geräteerkennung**: Intelligente Zuordnung von Benutzeränfragen zu Smart-Home-Geräten
- **Weboberfläche**: Benutzerfreundliches Frontend mit Streamlit
- **NLP-Verarbeitung**: Erweiterte Textverarbeitung mit spaCy und NLTK
- **Mehrsprachig**: Vollständige Unterstützung für deutsche Sprachmodelle

## Voraussetzungen

- Docker und Docker Compose (für Docker-Installation)
- Python 3.x und Poetry (für lokale Installation)
- Home Assistant-Instanz mit gültigem Token

## Installation

### Option 1: Docker (empfohlen)

#### 1. Repository klonen
```bash
git clone https://github.com/Kona418/NLP-Assistant.git
cd nlp-assitant
```

#### 2. Docker Compose konfigurieren

Bearbeite die `docker-compose.yml` und passe die Umgebungsvariablen an:

```yaml
environment:
  - HA_TOKEN=dein_home_assistant_token
  - KEYWORD=Jarvis
  - HA_URL=http://000.000.00.00:0000 # Platzhalter -> Eigene Home Assistant URL
```

**Home Assistant Token erstellen:**
1. In Home Assistant: Profil → Sicherheit → Token für den Langzeitzugriff
2. Namen eingeben und Token kopieren
3. Token in der `docker-compose.yml` eintragen

#### 3. Container starten
```bash
docker-compose up -d
```

Der Container wird automatisch gebaut und gestartet. Die Anwendung ist unter **http://localhost:8501** erreichbar.

### Option 2: Poetry (lokal)

#### 1. Repository klonen
```bash
git clone https://github.com/Kona418/NLP-Assistant.git
cd nlp-assitant
```

#### 2. Abhängigkeiten installieren
```bash
poetry install
```

#### 3. Umgebungsvariablen setzen
```bash
export HA_TOKEN=dein_home_assistant_token
export KEYWORD=Jarvis
export HA_URL=http://000.000.00.00:0000
```

#### 4. Anwendung starten
```bash
poetry run streamlit run app.py
```

Die Anwendung ist unter **http://localhost:8501** erreichbar.

## Verwendung

### Docker

#### Container starten
```bash
docker-compose up -d
```

#### Container stoppen
```bash
docker-compose down
```

### Poetry

#### Anwendung starten
```bash
poetry run streamlit run src\nlp_assistant\frontend\frontend.py
```

Die Weboberfläche ist unter **http://localhost:8501** erreichbar.