import dotenv
import spacy
from faster_whisper import WhisperModel


class SpeechPreProcessing:
    def __init__(self):
        dotenv.load_dotenv()

        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.nlp = spacy.load("de_core_news_sm")
        self.KEYWORD = dotenv.get_key(dotenv.find_dotenv(), "KEYWORD").lower().strip()


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
            sentences = list(doc.sents)


            for i, sentence in enumerate(sentences):
                sentence_text = sentence.text.strip()
                sentence_lower = sentence_text.lower()

                if self.KEYWORD in sentence_lower:
                    # Position direkt nach dem Keyword
                    position = sentence_lower.find(self.KEYWORD) + len(self.KEYWORD)
                    textAfterKeyword = sentence_text[position:].strip()

                    if textAfterKeyword:
                        first_char = textAfterKeyword[0]
                        
                        # Wenn nach dem Keyword ein Satzende ist -> nächsten Satz
                        if first_char [0] in '.!?':
                            if i + 1 < len(sentences):
                                return sentences[i + 1].text.strip()
                            return ""
                                                                                    
                        # Wenn nach dem Keyword ein Komma ist -> alles danach im Satz
                        elif first_char in ',':
                            return textAfterKeyword[1:].strip()  # überspringt das Trennzeichen
                        
                        # Wenn der Satz direkt nach dem Keyword folgt -> Rest des Satzes
                        else:
                            return textAfterKeyword.strip()

                else:
                    print(f"Keyword nicht im Satz gefunden: {sentence_text}")

        except Exception as e:
            print("Fehler bei der Extraktion des relevanten Satzes:", str(e))
        return ""