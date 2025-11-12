import whisper


class TextToSpeech:
    def __init__(self):
        self.model = whisper.load_model("base")

    def transcribeAudioToText(self, audio_path: str) -> str:
        """
        Transkribiert eine Audiodatei zu Text.
        
        Args:
            audio_path (str): Pfad zur Audiodatei.
        Returns:
            str: Transkripierte Text als String.

        """
        resultText = self.model.transcribe(audio_path)
        return resultText["text"]