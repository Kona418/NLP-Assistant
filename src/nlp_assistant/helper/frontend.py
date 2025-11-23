import time
import streamlit as st
import os

from nlp_assistant.backend import AssistantEngine
from nlp_assistant.helper.SpeechPreProcessing import SpeechPreProcessing

# Importiere das neue Backend (Pfad ggf. anpassen, je nach Ordnerstruktur)

AUDIO_FOLDER = "src/nlp_assistant/data/audio/" 
# Sicherstellen, dass der Ordner existiert
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Backend Initialisierung (Cached!)
# ---------------------------------------------------------
@st.cache_resource
def get_assistant_engine():
    """Lädt das NLP Backend nur einmalig beim Start."""
    return AssistantEngine()

try:
    engine = get_assistant_engine()
except Exception as e:
    st.error(f"Fehler beim Laden des Backends: {e}")
    st.stop()

# ---------------------------------------------------------
# UI Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="HomeAssistant Communication",
    page_icon="🎙️",
    layout="centered"
)

st.title("HomeAssistant NLP Controller")

# ---------------------------------------------------------
# Audio Input
# ---------------------------------------------------------
audio_bytes = st.audio_input(
    label="Drücke den Mikrofon Button, um die Aufnahme zu starten:",
    sample_rate=16000 
)

transkript_container = st.container()
status_container = st.empty()

# ---------------------------------------------------------
# Verarbeitungs-Logik
# ---------------------------------------------------------
if audio_bytes is not None:
    FILENAME = f"Aufnahme_{int(time.time())}.wav" # WAV ist oft sicherer für rohe Audio-Bytes
    FILEPATH = os.path.join(AUDIO_FOLDER, FILENAME)

    # 1. Datei speichern
    with open(FILEPATH, "wb") as f:
        f.write(audio_bytes.read())
    
    status_container.info("Verarbeite Audio...")

    # 2. Transkription (Whisper o.ä.)
    try:
        pre_processor = SpeechPreProcessing()
        # Annahme: transcribeAudioToText akzeptiert Pfad
        full_transkript = pre_processor.transcribeAudioToText(str(FILEPATH))
        
        # Extraktion des relevanten Satzes (falls nötig)
        relevanter_satz = pre_processor.extractTheRelevantSentence(full_transkript)
        
        transkript_container.success(f"🗣️ Erkannt: **{relevanter_satz}**")

        # 3. An das Backend senden (Die "Magie")
        with st.spinner("Sende Befehl an Home Assistant..."):
            result = engine.process_command(relevanter_satz)

        # 4. Ergebnis anzeigen
        if result["status"] == "success":
            st.balloons()
            st.success(f"✅ Aktion ausgeführt!")
            st.json(result) # Zeigt Details wie Intent, Device und Zeit an
        else:
            st.error(f"❌ Fehler: {result.get('message', 'Unbekannter Fehler')}")

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")

    finally:
        # Aufräumen
        if os.path.exists(FILEPATH):
            os.unlink(FILEPATH)