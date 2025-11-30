import dotenv
import spacy
from faster_whisper import WhisperModel
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

class SpeechPreProcessing:
    def __init__(self) -> None:
        # Transkriptionsmodell initialisieren
        self.model = WhisperModel("turbo", device="cpu", compute_type="int8")
        
        # Satzextraktion initialisieren         
        self.nlp = spacy.load("de_core_news_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Laden des Keywords aus der .env Datei
        dotenv.load_dotenv()
        self.KEYWORD = dotenv.get_key(dotenv.find_dotenv(), "KEYWORD").lower().strip()

        # Keyword vorbereiten
        cleaned_keyword = self.KEYWORD.lower().strip()
        keyword_doc = self.nlp(cleaned_keyword, disable=["tagger", "parser", "ner"])

        # Das Schlüsselwort dem Matcher hinzufügen
        self.matcher.add("COMMAND_KEYWORD", [keyword_doc])


    def transcribeAudioToText(self, audio_path: str) -> str:
            """
            Transkribiert eine Audiodatei zu Text.
            
            Args:
                audio_path (str): Pfad zur Audiodatei.
            Returns:
                str: Transkripierter Text als String.
            """
            try:
                segments, info = self.model.transcribe(audio_path, language='de')

                text_segments = [segment.text for segment in segments]
                full_text = "".join(text_segments).strip()
                return full_text
            
            except Exception as e:
                print("Fehler bei der Transkription:", str(e))
                return ""


    def extractTheRelevantSentence(self, transcript: str) -> str:
        """
        Extrahiert den relevanten Satz (Befehl) basierend auf dem Schlüsselwort.
        Args:
            transcript (str): Transkribierter Text.
        Returns:
            str: Relevanter Satz (Befehl) nach dem Schlüsselwort.
        """

        try:
            # NLP-Dokument erstellen und Sätze extrahieren
            doc = self.nlp(transcript)
            sentences: list[Span] = list(doc.sents)

            for i, sentence_span in enumerate(sentences):
                matches = self.matcher(sentence_span)

                if matches:
                    _, start_token, end_token = matches[0]

                    # Position direkt nach dem Keyword
                    text_after_keyword_span = sentence_span[end_token:]
                    textAfterKeyword = text_after_keyword_span.text.strip()

                    if not textAfterKeyword:
                        # Wenn kein Text nach dem Keyword im Satz ist -> nächsten Satz
                        if i + 1 < len(sentences):
                            return sentences[i + 1].text.strip()
                        # Wenn kein weiterer Satz existiert
                        return ""
                        
                    # Erster Charakter nach dem Keyword
                    first_char = textAfterKeyword[0]
                        
                    # Wenn nach dem Keyword ein Satzende ist -> nächsten Satz
                    if first_char in '.!?':
                        if i + 1 < len(sentences):
                            return sentences[i + 1].text.strip()
                        return ""
                                                                                    
                    # Wenn nach dem Keyword ein Komma ist -> alles danach im Satz
                    elif first_char in ',':
                        return textAfterKeyword[1:].strip()
                        
                    # Wenn der Satz direkt nach dem Keyword folgt -> Rest des Satzes
                    else:
                        return textAfterKeyword.strip()

            print(f"Es wurde kein Match für das Keyword '{self.KEYWORD}' in der Transkription gefunden.")
            return ""
        
        except Exception as e:
            print("Fehler bei der Extraktion des relevanten Satzes:", str(e))
        return ""