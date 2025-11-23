import time
import streamlit as st
import os

from nlp_assistant.backend import backend
from nlp_assistant.helper.SpeechPreProcessing import SpeechPreProcessing

AUDIO_FOLDER = "src/nlp_assistant/data/audio/"


class FrontendApp:
    def __init__(self) -> None:
        self.backend_manager = backend()
        self.speech = SpeechPreProcessing()

    def run(self) -> None:
        st.set_page_config(
            page_title="HomeAssistant Communication",
            page_icon="🎙️",
            layout="centered"
        )

        st.title("HomeAssistant Communication")

        st.subheader("User Input:")
        # Textinput zuerst, damit er immer aktiv ist
        user_input = st.text_input("Gebe hier bitte dein Befehl ein", "")

        # Audioaufnahme
        audio_bytes = st.audio_input(
            label="Drücke den Mikrofon Button, um die Aufnahme zu starten:",
            sample_rate=16000
        )

        st.subheader("Ergebnisse:")

        progress = st.empty()

        platzhalter_transkript = st.empty()
        platzhalter_relevanter_satz = st.empty()
        platzhalter_intent = st.empty()
        platzhalter_device = st.empty()
        platzhalter_action = st.empty()

        st.divider()
        platzhalter_popup = st.empty()

        relevanter_satz = None
        # Wenn Audio vorhanden ist, speichern und transkribieren
        if audio_bytes is not None:
            os.makedirs(AUDIO_FOLDER, exist_ok=True)
            filepath = os.path.join(AUDIO_FOLDER, f"Aufnahme_{int(time.time())}.mp3")

            with open(filepath, "wb") as f:
                f.write(audio_bytes.read())

            platzhalter_popup.success("Audioaufnahme erfolgreich gespeichert!")
            progress.progress(10)

            try:
                transkript = self.speech.transcribeAudioToText(filepath)
                platzhalter_transkript.code(f"Transkript: {transkript}", language="text")
                platzhalter_popup.success("Audioaufnahme erfolgreich transkribiert!")
                progress.progress(25)

                relevanter_satz = self.speech.extractTheRelevantSentence(transkript)
                platzhalter_relevanter_satz.code(f"Relevanter Satz: {relevanter_satz}", language="text")
                platzhalter_popup.success("Befehl erfolgreich extrahiert!")
                progress.progress(50)

            except Exception as e:
                platzhalter_popup.error(f"Fehler in der Spracherkennung oder Satzextraktion: {e}")

            if os.path.exists(filepath):
                os.unlink(filepath)
        
        relevanterSatzfürsBackend = (relevanter_satz.strip() if relevanter_satz else user_input.strip())
    
        if relevanterSatzfürsBackend:
            try:
                intent, raw_device_name, device_name, action_input = self.backend_manager.process_command(
                    relevanterSatzfürsBackend
                )
                progress.progress(75)

                platzhalter_intent.code(f"Erkannter Intent: {intent}", language="text")
                platzhalter_device.code(f"Erkanntes Gerät: {device_name}", language="text")
                platzhalter_action.code(f"Auszuführende Aktion: {action_input}", language="text")

                if action_input.get("success", False):
                    platzhalter_popup.success(f"Aktion erfolgreich ausgeführt: {action_input}")
                else:
                    platzhalter_popup.warning(f"Aktion nicht erfolgreich ausgeführt: {action_input}")

                progress.progress(100)

            except Exception as e:
                platzhalter_popup.error(f"Fehler in der Backend-Verarbeitung: {e}")
        else:
            platzhalter_popup.warning("Bitte gib einen Text ein oder nimm Audio auf.")


if __name__ == "__main__":
    FrontendApp().run()
