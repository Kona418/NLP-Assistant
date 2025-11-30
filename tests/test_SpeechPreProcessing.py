import pytest

from src.nlp_assistant.backend.audio.SpeechPreProcessing import SpeechPreProcessing

class TestTextToSpeech:
    TEST_AUDIO_PATH = [["src/nlp_assistant/data/audio/heizungAuf20Grad.m4a", "Stelle die Heizung auf 20 Grad im Wohnzimmer."],
                       ["src/nlp_assistant/data/audio/schalteDasLichtAn.mp3", "Schalte das Licht an."]]
    
    TEST_EXTRACT_SENTENCE = [["Hallo Jarvis. Stelle die Heizung auf 20 Grad im Wohnzimmer. Danke!", "Stelle die Heizung auf 20 Grad im Wohnzimmer."],
                             ["Jarvis, schalte bitte das Licht an.", "schalte bitte das Licht an."], 
                             ["Guten Morgen Jarvis! Stelle die Lampe im Wohnzimmer auf 50%?", "Stelle die Lampe im Wohnzimmer auf 50%?"],
                             ["Hey Jarvis aktiviere den Switch im Schlafzimmer, bitte. Nicht relevanter Satz", "aktiviere den Switch im Schlafzimmer, bitte."],]


    @pytest.mark.parametrize("audio_path, expected_text", TEST_AUDIO_PATH)
    def testAudioToTextConversion(self, audio_path: str, expected_text: str):
        """
        Testet die Speech-to-Text Konvertierung.
        Jedes Element in TEST_AUDIO_PATH wird dabei als separater Testfall ausgeführt.
        """

        # Audio zu Text konvertieren
        converted_text = SpeechPreProcessing().transcribeAudioToText(audio_path)

        # Gibt eine Fehlermeldung bei falscher Konvertierung aus
        assert (converted_text == expected_text), \
        f"FEHLER: Audio:'{audio_path}' Transkripierter Text: '{converted_text}' Korrekter Text: '{expected_text}'"


    @pytest.mark.parametrize("transcript, expected_sentence", TEST_EXTRACT_SENTENCE)
    def testExtractTheRelevantSentence(self, transcript: str, expected_sentence: str):
        """
        Testet die Extraktion des relevanten Satzes (Befehl) aus einem Transkript.
        """

        # Relevanten Satz extrahieren
        relevant_sentence = SpeechPreProcessing().extractTheRelevantSentence(transcript)

        # Gibt eine Fehlermeldung bei falscher Extraktion aus
        assert (relevant_sentence == expected_sentence), \
        f"FEHLER: Transkript:'{transcript}' Extrahierter Satz: '{relevant_sentence}' Korrekter Satz: '{expected_sentence}'"
