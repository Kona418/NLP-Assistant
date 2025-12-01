import json
import time
import streamlit as st
import os

from nlp_assistant.backend.backendController import backendController
from nlp_assistant.backend.audio.SpeechPreProcessing import SpeechPreProcessing

AUDIO_FOLDER = "src/nlp_assistant/data/audio/"

# =========================================================================
# Backend Services - Initialisierung (Einmalig)
# =========================================================================
@st.cache_resource
class BackendServices:
    """
    Diese Klasse initialisiert rechenintensive Objekte nur EINMAL 
    (Cache Resource) und gibt sie bei jedem Rerun wieder.
    """
    def __init__(self):
        self.backend_manager = backendController()
        self.speech = SpeechPreProcessing()

# =========================================================================
# Frontend Klasse
# =========================================================================
class FrontendApp:
    def __init__(self) -> None:

        # Initialisiere Backend Services
        self.services = BackendServices()
        
        # Initialisiere Ergebnisse im Session State
        if "results" not in st.session_state:
            st.session_state.results = {}
        
        # Initialisiere einen Zähler für den Audio-Widget-Key -> Für Reset des Audio-Widgets
        if "audio_key_id" not in st.session_state:
            st.session_state.audio_key_id = 0

    def process_data(self, ladeIcon_placeholder) -> None  :
        """
        Führt die gesamte Verarbeitung des Inputs aus.

        """
        with ladeIcon_placeholder.container():
            with st.spinner('Verarbeite die Eingabe... Bitte warten Sie einen Moment.'):
                # Wir greifen auf die initialisierten Dienste zu
                backend_manager = self.services.backend_manager
                speech = self.services.speech
                # --- IDs/Keys generieren zum Zurücksetzen des Audio-Widgets ---
                current_audio_key = f"audio_input_{st.session_state.audio_key_id}"
                    
                # User Input aus Session State laden
                user_input_text = st.session_state.get("text_input_key", "")
                audio_bytes = st.session_state.get(current_audio_key, None)
                    
                relevanter_satz = None
                st.session_state.results = {}
                    
                # --- Audio Input ---
                if audio_bytes is not None:
                    # Speichere die Audioaufnahme temporär ab
                    os.makedirs(AUDIO_FOLDER, exist_ok=True)
                    filepath = os.path.join(AUDIO_FOLDER, f"Aufnahme_{int(time.time())}.mp3")

                    try:
                        # Öffne die Datei und schreibe die Bytes hinein
                        with open(filepath, "wb") as f:
                            f.write(audio_bytes.read())
                            
                        # Verarbeite die Audiodatei
                        transkript = speech.transcribeAudioToText(filepath)
                        st.session_state.results["transkript"] = transkript
                        
                        # Extrahiere den relevanten Satz aus dem Transkript
                        relevanter_satz = speech.extractTheRelevantSentence(transkript)
                        st.session_state.results["relevanter_satz"] = relevanter_satz
                        st.session_state.results["audio_success"] = True

                    except Exception as e:
                        st.session_state.results["error"] = f"Fehler in der Spracherkennung: {e}"

                    finally:
                        if os.path.exists(filepath):
                            os.unlink(filepath)

                # --- Text Input ---
                elif user_input_text.strip() != "":
                    # Extrahiere den relevanten Satz aus dem Texteingabe
                    relevanter_satz = speech.extractTheRelevantSentence(user_input_text.strip())

                    # Wenn kein Keyword verwendet wurde, gesamten Text als Befehl nutzen
                    if relevanter_satz == "":
                        relevanter_satz = user_input_text.strip()

                    st.session_state.results["relevanter_satz"] = relevanter_satz

                # --- Backend Verarbeitung des relevanten Satzes ---
                if relevanter_satz:
                    try:
                        intent, raw_device_name, device_name, action_input = backend_manager.process_command(
                            relevanter_satz
                        )
                        st.session_state.results["intent"] = intent
                        st.session_state.results["device_name"] = device_name
                        st.session_state.results["action_input"] = action_input
                        st.session_state.results["backend_success"] = action_input.get("success", False)

                    except Exception as e:
                        st.session_state.results["backend_error"] = f"Fehler im Backend: {e}"
                    
                # --- Reset des Audio und Text Inputs ---
                st.session_state["text_input_key"] = ""
                st.session_state.audio_key_id += 1
                

    def run(self) -> None:
        #################################################################################
        # STREAMLIT CONFIG 
        #################################################################################
        st.set_page_config(page_title="HomeAssistant Communication", page_icon="🎙️", layout="centered")
        st.title("HomeAssistant Communication")

        # Ergebnisse aus Session State laden
        results = st.session_state.get("results", {})

        # Tabs erstellen
        tab_input, tab_results = st.tabs(["Userinput", "Ergebnisse & Details"])

        #################################################################################
        # USER INPUT
        #################################################################################
        with tab_input:
            st.info('Verwende das Keyword "Jarvis" und gebe anschließend den auszuführenden Befehl an.')

            # Text Input
            st.text_input("Gebe hier bitte dein Befehl ein:", key="text_input_key")

            # Audio Input mit dynamischem session key
            dynamic_key = f"audio_input_{st.session_state.audio_key_id}"
            
            st.audio_input(
                label="Drücke den Mikrofon Button, um die Aufnahme zu starten:",
                sample_rate=16000,
                key=dynamic_key
            )

            ladeIcon_placeholder = st.empty()

            # Run Button
            st.button("Befehl ausführen", on_click=self.process_data, type="primary", use_container_width=True, args=[ladeIcon_placeholder])

            # Erfolgs- und Fehlermeldungen der Backend Aktion
            if results.get("backend_success"):
                st.success(f"Aktion erfolgreich ausgeführt.")
            else:
                st.warning(f"Aktion nicht erfolgreich ausgeführt.")
            

            if "error" in results:
                st.error(results["error"])
            
            if "backend_error" in results:
                st.error(results["backend_error"])

        #################################################################################
        # ERGEBNISSE ANZEIGEN
        #################################################################################
        with tab_results:

            # Transkript anzeigen
            if "transkript" in results:
                st.code(f"Transkript: {results['transkript']}", language="text")

            # Befehl anzeigen
            if "relevanter_satz" in results:
                st.code(f"Befehl: {results['relevanter_satz']}", language="text")
                
            if "intent" in results:
                # Backend Aktion
                action_data = json.dumps(results.get("action_input", {}), indent=4)
                st.code(f"Backend Aktion: {action_data}", language="json")

                # Erkanntes Gerät
                device_data = json.dumps(results.get("device_name", {}), indent=4)
                st.code(f"Erkanntes Gerät: {device_data}", language="json")

if __name__ == "__main__":
    FrontendApp().run()