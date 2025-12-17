import dotenv
import spacy
import os
import sys
from faster_whisper import WhisperModel
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

# --- FIX FÜR POETRY/WINDOWS ---
# Fügt die Nvidia-Libs temporär zum PATH hinzu, damit CTranslate2 sie findet.
# Dies muss VOR der Initialisierung von WhisperModel passieren.
def _add_nvidia_paths():
    try:
        import nvidia.cudnn
        import nvidia.cublas
    except ImportError:
        return

    # Ermittlung der Pfade über __path__ (Liste), falls __file__ None ist
    def get_module_path(module):
        if hasattr(module, "__file__") and module.__file__:
            return os.path.dirname(module.__file__)
        if hasattr(module, "__path__"):
            return module.__path__[0]
        return None

    cudnn_path = get_module_path(nvidia.cudnn)
    cublas_path = get_module_path(nvidia.cublas)
    
    paths_to_add = []
    if cudnn_path:
        paths_to_add.append(os.path.join(cudnn_path, 'bin'))
    if cublas_path:
        paths_to_add.append(os.path.join(cublas_path, 'bin'))
    
    for path in paths_to_add:
        if os.path.exists(path):
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(path)
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

_add_nvidia_paths()
# ------------------------------

class SpeechPreProcessing:
    def __init__(self) -> None:
        # Transkriptionsmodell initialisieren
        # RTX 2070 unterstützt float16, das ist präziser als int8. 
        # Falls VRAM knapp ist, bleib bei "int8".
        print("Lade Whisper Model...")
        self.model = WhisperModel("turbo", device="cuda", compute_type="float16")
        
        # Satzextraktion initialisieren
        try:
            self.nlp = spacy.load("de_core_news_sm")
        except OSError:
            raise OSError("SpaCy Modell nicht gefunden. Bitte führe aus: python -m spacy download de_core_news_sm")
            
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Laden des Keywords aus der .env Datei
        dotenv.load_dotenv()
        self.KEYWORD = os.getenv("KEYWORD", "jarvis").lower().strip()

        # Keyword vorbereiten
        cleaned_keyword = self.KEYWORD.lower().strip()
        keyword_doc = self.nlp(cleaned_keyword, disable=["tagger", "parser", "ner"])

        # Das Schlüsselwort dem Matcher hinzufügen
        self.matcher.add("COMMAND_KEYWORD", [keyword_doc])

    def transcribeAudioToText(self, audio_path: str) -> str:
        """Transkribiert eine Audiodatei zu Text."""
        try:
            # beam_size=5 erhöht die Genauigkeit leicht
            segments, info = self.model.transcribe(audio_path, language='de', beam_size=5)

            text_segments = [segment.text for segment in segments]
            full_text = "".join(text_segments).strip()
            return full_text
        
        except Exception as e:
            print(f"Fehler bei der Transkription: {e}")
            return ""

    def extractTheRelevantSentence(self, transcript: str) -> str:
        """Extrahiert den relevanten Satz (Befehl) basierend auf dem Schlüsselwort."""
        try:
            doc = self.nlp(transcript)
            sentences: list[Span] = list(doc.sents)

            for i, sentence_span in enumerate(sentences):
                matches = self.matcher(sentence_span)

                if matches:
                    _, start_token, end_token = matches[0]
                    
                    # Text nach dem Keyword
                    text_after_keyword_span = sentence_span[end_token:]
                    textAfterKeyword = text_after_keyword_span.text.strip()

                    if not textAfterKeyword:
                        # Keyword am Satzende -> Nächster Satz ist der Befehl
                        if i + 1 < len(sentences):
                            return sentences[i + 1].text.strip()
                        return ""
                        
                    first_char = textAfterKeyword[0]
                        
                    # Satzzeichen-Check
                    if first_char in '.!?':
                        if i + 1 < len(sentences):
                            return sentences[i + 1].text.strip()
                        return ""
                    elif first_char in ',':
                        return textAfterKeyword[1:].strip()
                    else:
                        return textAfterKeyword.strip()

            print(f"Kein Match für '{self.KEYWORD}' gefunden.")
            return ""
        
        except Exception as e:
            print(f"Fehler bei der Extraktion: {e}")
            return ""