from tabnanny import check
import time
import streamlit as st
import os 

from nlp_assistant.helper.SpeechPreProcessing import SpeechPreProcessing

AUDIO_FOLDER = "src/nlp_assistant/data/audio/" 
FILENAME = f"Aufnahme_{int(time.time())}.mp3"
FILEPATH = AUDIO_FOLDER + FILENAME

class FrontendApp:
    ####################################
    # Config
    ####################################

    st.set_page_config(
        page_title="HomeAssistant Communication",
        page_icon="🎙️",
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


    st.divider()

    popUpMeldungenPlatzhalter = st.empty()

    ####################################
    # Logik 
    ####################################

    start_time = time.time()
    if audio_bytes is not None:
        
        ## Speichern der Audiodatei
        with open(FILEPATH, "wb") as f:
            f.write(audio_bytes.read())
        popUpMeldungenPlatzhalter.success("Audioaufnahme erfolgreich gespeichert!")

        ## Transkription
        transkript = SpeechPreProcessing().transcribeAudioToText(str(FILEPATH))
        popUpMeldungenPlatzhalter.success("Audioaufnahme erfolgreich transkribiert!")
        
        ## Ausgabe
        transkriptPlatzhalter.code(f"Transkript: {transkript}", language="text")
        print("Saved temporary Voicefile:", FILEPATH)


        ## Löschen der Audiodatei            
        if os.path.exists(str(FILEPATH)):
            os.unlink(FILEPATH)
            print(f"Temporäre Datei gelöscht: {FILEPATH}")
        
        ## Extraktion des relevanten Satzes
        relevanterSatz = SpeechPreProcessing().extractTheRelevantSentence(transkript)
        relevanterSatzPlatzhalter.code(f"Relevanter Satz: {relevanterSatz}", language="text")
        popUpMeldungenPlatzhalter.success("Befehl erfolgreich extrahiert!")
