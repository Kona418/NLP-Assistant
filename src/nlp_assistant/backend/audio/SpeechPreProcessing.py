import os
import logging
import importlib
import dotenv
import spacy
import torch
from faster_whisper import WhisperModel
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

# Logging Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _patch_nvidia_paths() -> None:
    """
    Fügt Nvidia CUDNN/CUBLAS Binaries temporär zum DLL-Suchpfad hinzu.
    Notwendig für CTranslate2 (Faster-Whisper) unter Windows/Poetry Umgebungen.
    """
    try:
        paths_to_add = []

        for lib_name in ['nvidia.cudnn', 'nvidia.cublas']:
            try:
                module = importlib.import_module(lib_name)
                # Fallback Strategie für Pfad-Ermittlung
                mod_path = getattr(module, '__file__', None)
                if mod_path:
                    base_path = os.path.dirname(mod_path)
                elif hasattr(module, '__path__'):
                    base_path = module.__path__[0]
                else:
                    continue
                
                bin_path = os.path.join(base_path, 'bin')
                if os.path.exists(bin_path):
                    paths_to_add.append(bin_path)
            except ImportError:
                continue

        for path in paths_to_add:
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(path)
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
            
    except Exception as e:
        logger.warning(f"Nvidia Path Patching fehlgeschlagen: {e}")

# Patch vor Laden des Models ausführen
_patch_nvidia_paths()


class SpeechPreProcessing:
    def __init__(self) -> None:
        # Prüfen auf verfügbare GPU
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
        else:
            device = "cpu"
            compute_type = "int8"

        print(f"Lade Whisper Model ({device})...")
        self.model = WhisperModel("turbo", device=device, compute_type=compute_type)
        
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