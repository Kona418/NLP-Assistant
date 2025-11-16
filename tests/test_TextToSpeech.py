import pytest
from regex import T

from src.nlp_assistant.helper.TextToSpeech import TextToSpeech

class TestTextToSpeech:
    TEST_AUDIO_PATH = [["src/nlp_assistant/data/audio/heizungAuf20Grad.m4a", "Stelle die Heizung auf 20 Grad im Wohnzimmer."],
                       ["src/nlp_assistant/data/audio/schalteDasLichtAn.mp3", "Schalte das Licht an."]]
    
    @pytest.mark.parametrize("audio_path, expected_text", TEST_AUDIO_PATH)
    def testAudioToTextConversion(self, audio_path: str, expected_text: str):
        """
        Testet die Speech-to-Text Konvertierung.
        Jedes Element in TEST_AUDIO_PATH wird dabei als separater Testfall ausgeführt.
        """

        # Audio zu Text konvertieren
        converted_text = TextToSpeech().transcribeAudioToText(audio_path)

        # Gibt eine Fehlermeldung bei falscher Konvertierung aus
        assert (converted_text == expected_text), \
        f"FEHLER: Audio:'{audio_path}' Transkripierter Text: '{converted_text}' Korrekter Text: '{expected_text}'"

