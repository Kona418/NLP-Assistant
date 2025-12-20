import dotenv
import spacy
import os
import sys
import platform # Wichtig für OS-Check
import torch    # Wichtig, sonst Crash bei torch.cuda.is_available()
from faster_whisper import WhisperModel
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

# --- FIX FÜR POETRY/WINDOWS ---
def _add_nvidia_paths():
    # Unter Linux/Docker sofort abbrechen, um Fehler zu vermeiden
    if platform.system() != "Windows":
        return

    try:
        import nvidia.cudnn
        import nvidia.cublas
    except ImportError:
        return

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

    # hashattr check verhindert Crash unter Linux, falls platform check versagt
    if hasattr(os, 'add_dll_directory'):
        for path in paths_to_add:
            if os.path.exists(path):
                try:
                    os.add_dll_directory(path)
                except Exception:
                    pass
                os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

_add_nvidia_paths()
# ------------------------------

class SpeechPreProcessing:
    def __init__(self) -> None:
        print("Lade Whisper Model...")
        if torch.cuda.is_available():
            print(f"GPU gefunden: {torch.cuda.get_device_name(0)}. Lade Whisper Model auf CUDA...")
            device = "cuda"
            compute_type = "float16"
        else:
            print("Keine Nvidia GPU gefunden oder CUDA nicht konfiguriert. Nutze CPU...")
            device = "cpu"
            compute_type = "int8"

        try:
            self.model = WhisperModel("turbo", device=device, compute_type=compute_type)
        except Exception as e:
            print(f"Fehler beim Laden des Modells: {e}")
            if device == "cuda":
                print("Versuche Fallback auf CPU...")
                self.model = WhisperModel("turbo", device="cpu", compute_type="int8")

        # Satzextraktion initialisieren
        try:
            self.nlp = spacy.load("de_core_news_sm")
        except OSError:
            raise OSError("SpaCy Modell nicht gefunden.")

        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        dotenv.load_dotenv()
        self.KEYWORD = os.getenv("KEYWORD", "jarvis").lower().strip()

        cleaned_keyword = self.KEYWORD.lower().strip()
        keyword_doc = self.nlp(cleaned_keyword, disable=["tagger", "parser", "ner"])

        self.matcher.add("COMMAND_KEYWORD", [keyword_doc])

    def transcribeAudioToText(self, audio_path: str) -> str:
        try:
            segments, info = self.model.transcribe(audio_path, language='de', beam_size=5)
            text_segments = [segment.text for segment in segments]
            full_text = "".join(text_segments).strip()
            return full_text
        except Exception as e:
            print(f"Fehler bei der Transkription: {e}")
            return ""

    def extractTheRelevantSentence(self, transcript: str) -> str:
        try:
            doc = self.nlp(transcript)
            sentences: list[Span] = list(doc.sents)

            for i, sentence_span in enumerate(sentences):
                matches = self.matcher(sentence_span)

                if matches:
                    _, start_token, end_token = matches[0]
                    text_after_keyword_span = sentence_span[end_token:]
                    textAfterKeyword = text_after_keyword_span.text.strip()

                    if not textAfterKeyword:
                        if i + 1 < len(sentences):
                            return sentences[i + 1].text.strip()
                        return ""

                    first_char = textAfterKeyword[0]

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


#Hello World