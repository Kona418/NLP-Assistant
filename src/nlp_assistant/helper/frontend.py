import time
import streamlit as st
import os


from nlp_assistant.backend import backend 
from nlp_assistant.helper.SpeechPreProcessing import SpeechPreProcessing

AUDIO_FOLDER = "src/nlp_assistant/data/audio/" 
FILENAME = f"Aufnahme_{int(time.time())}.mp3"
FILEPATH = AUDIO_FOLDER + FILENAME

class FrontendApp:
    def __init__(self):
        # Initialisierung des Backend-Managers
        self.backend_manager = backend()

    def run(self):
        ####################################
        # Config
        ####################################

        st.set_page_config(
            page_title="HomeAssistant Communication",
            page_icon="🎙",
            layout="centered"
        )

        st.title("HomeAssistant Communication")


        ####################################
        # Webinhalt 
        ####################################

        audio_bytes = st.audio_input(
            label="Drücke den Mikrofon Button, um die Aufnahme zu starten:",
            sample_rate=16000 
        )

        transkriptPlatzhalter = st.empty()
        relevanterSatzPlatzhalter = st.empty()
        intentPlatzhalter = st.empty()
        devicePlatzhalter = st.empty()


        st.divider()

        popUpMeldungenPlatzhalter = st.empty()

        ####################################
        # Logik 
        ####################################

        if audio_bytes is not None:
            
            ## Temporäre Audio-Datei speichern
            # Stelle sicher, dass der Audio-Ordner existiert
            os.makedirs(AUDIO_FOLDER, exist_ok=True)
            with open(FILEPATH, "wb") as f:
                f.write(audio_bytes.read())
            popUpMeldungenPlatzhalter.success("Audioaufnahme erfolgreich gespeichert!")

            # --- VORVERARBEITUNG: Transkription und Extraktion des relevanten Satzes ---
   
            try:
                # Transkription
                transkript = SpeechPreProcessing().transcribeAudioToText(str(FILEPATH))
                transkriptPlatzhalter.code(f"Transkript: {transkript}", language="text")
                popUpMeldungenPlatzhalter.success("Audioaufnahme erfolgreich transkribiert!")
                
                # Extraktion des relevanten Satzes
                relevanterSatz = SpeechPreProcessing().extractTheRelevantSentence(transkript)
                relevanterSatzPlatzhalter.code(f"Relevanter Satz: {relevanterSatz}", language="text")
                popUpMeldungenPlatzhalter.success("Befehl erfolgreich extrahiert!")
                
            except Exception as e:
                popUpMeldungenPlatzhalter.error(f"Fehler in der Spracherkennung/Extraktion: {e}")
                relevanterSatz = None

            
            # --- BACKEND-VERARBEITUNG: Intent, Gerät und Aktion ausführen ---
            if relevanterSatz:
                try:
                    # Der BackendManager übernimmt nun die Logik aus der alten 'backend' Klasse
                    ergebnis = self.backend_manager.process_command(relevanterSatz)
                    
                    # Ausgabe der extrahierten Informationen
                    intentPlatzhalter.code(f"Erkannter Intent (Service): {ergebnis.get('service', 'Nicht erkannt')}", language="text")
                    devicePlatzhalter.code(f"Erkanntes Gerät (Name/Typ): {ergebnis.get('name', 'Nicht erkannt')} / {ergebnis.get('domain', 'Nicht erkannt')}", language="text")
                    
                    if ergebnis.get('success', False):
                        popUpMeldungenPlatzhalter.success(f"Aktion erfolgreich ausgeführt: {ergebnis['message']}")
                    else:
                        popUpMeldungenPlatzhalter.warning(f"Aktion nicht ausgeführt: {ergebnis['message']}")
                        
                except Exception as e:
                    popUpMeldungenPlatzhalter.error(f"Fehler in der Backend-Verarbeitung: {e}")
            
            # --- Aufräumarbeiten ---
            if os.path.exists(str(FILEPATH)):
                os.unlink(FILEPATH)
 

if __name__ == "__main__":
    app = FrontendApp()
    app.run()