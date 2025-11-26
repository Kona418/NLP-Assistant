import spacy
from nltk.metrics import edit_distance

class DeviceMatcher:

    def __init__(self, SIMILARITY_THRESHOLD=0.5) -> None:
        
        self.SIMILARITY_THRESHOLD = SIMILARITY_THRESHOLD

        try:
            self.nlp = spacy.load("de_core_news_lg")
        except OSError:
            from spacy.cli import download
            download("de_core_news_lg")
            self.nlp= spacy.load("de_core_news_lg")
        
    @staticmethod
    def cleanString(s: str) -> str:
        """Reinigt den String für den Abgleich."""
        return s.lower().replace("-", " ").replace("_", " ").strip()
    

    def findBestDeviceMatch(self, targetDeviceName: str, deviceList: list) -> dict | None:
        """
        Findet das beste passende Gerät aus der Geräteliste basierend auf dem Gerätenamen.

        Args:
            device_name (str): Name des Geräts, das abgeglichen werden soll.
            deviceList (list): Liste der verfügbaren Geräte.

        Returns:
            dict | None: Das beste passende Gerät oder None, wenn kein passendes Gerät gefunden wurde.
        """

        # Initialisierung
        best_match_Vector: dict | None = None
        best_match_Levenshtein: dict | None = None
        highest_Vector_similarity: float = 0.0
        highest_Levenshtein_Similarity: float = 0.0

        clean_targetDeviceName: str = self.cleanString(targetDeviceName)
        targetDeviceName_doc: spacy.tokens.Doc = self.nlp(clean_targetDeviceName)

        if  clean_targetDeviceName == "" or len(deviceList) == 0:
            print("Kein Gerätename zum Abgleichen angegeben.")
            return None
        
        for device in deviceList:
            clean_device_name: str = self.cleanString(device['name'])

            # 1. Vektor Similarity
            device_doc: spacy.tokens.Doc = self.nlp(clean_device_name)
            similarity_Vector: float = targetDeviceName_doc.similarity(device_doc)

            if similarity_Vector > highest_Vector_similarity:
                highest_Vector_similarity = similarity_Vector
                best_match_Vector = device

            # 2. Normalisierte Levenshtein-Distanz
            distanz = edit_distance(clean_device_name, clean_targetDeviceName)
            max_len = max(len(clean_device_name), len(clean_targetDeviceName))
            
            similarity_Ratio_Levenshtein: float = 1.0 - (distanz / max_len)  
            
            if similarity_Ratio_Levenshtein > highest_Levenshtein_Similarity:
                highest_Levenshtein_Similarity = similarity_Ratio_Levenshtein
                best_match_Levenshtein = device


        # Überprüfung, ob die höchste Ähnlichkeit über dem Schwellenwert liegt 
        # 1. Vektor Similarity 
        # 2. Levenshtein Similarity
        if highest_Vector_similarity >= self.SIMILARITY_THRESHOLD:
            print(f"Bestes Match für: '{targetDeviceName}' =  '{best_match_Vector['name']}' mit einer Similartiy von {highest_Vector_similarity:.2f}")
            return best_match_Vector
        
        elif highest_Levenshtein_Similarity >= self.SIMILARITY_THRESHOLD:
            print(f"Bestes Match für: '{targetDeviceName}' =  '{best_match_Levenshtein['name']}' mit einer Levinshtein-Similarity von {highest_Levenshtein_Similarity:.2f}")
            return best_match_Levenshtein
        
        else:
            print(f"Es wurde kein Match für das Gerät '{targetDeviceName}' gefunden.")
            print(f"Levenshtein-Similarity: {highest_Levenshtein_Similarity:.2f}, Vector-Similarity: {highest_Vector_similarity:.2f}")
            return None
            

    def extractDeviceNamesFromCommands(self, command: str) -> str:
        """
        Extrahiert den DeviceName aus dem Sprachbefehl.
        Strategie: Finde den grammatikalischen Kern des Objekts (egal ob NOUN oder X) und sammle alle dazugehörigen Wörter ein.
        Args:
            command (str): Der Sprachbefehl.
        Returns:
            str: Der extrahierte DeviceName.
            
        """
        doc = self.nlp(command)
        
        # Definiere relevante Abhängigkeitsbeziehungen
        target_deps: list[str] = ["oa", "obj", "dobj", "sb", "nsubj", "pd"]
        
        # Sammle potenzielle Kandidaten
        candidates: list[tuple[int, str]] = []

        for token in doc:
            # 1. Finde Tokens mit den relevanten Dependencies
            if token.dep_ in target_deps:
                
                # 2. Gehe den Baum runter und sammle relevante Wörter ein
                relevant_words: list[str] = []
                
                # Über den Subtree des gefundenen Tokens iterieren
                for sub_token in token.subtree:
                    
                    # Filtere nur relevante Wortarten heraus -> Keine Artikel, Pronomen, Satzzeichen, Präpositionen
                    if sub_token.pos_ not in ["DET", "PRON", "PUNCT", "ADP"]:
                        
                        # Präpositionen ausschließen -> Ort, Zeit
                        if sub_token.head.pos_ == "ADP":
                            continue
                            
                        relevant_words.append(sub_token.text)

                if relevant_words:
                    # Die relevanten Wörter zu einem String zusammenfügen -> ["TV" "Steckdose"] -> "TV Steckdose"
                    phrase: str = " ".join(relevant_words)
                    
                    # Setze die Priorität basierend auf der Dependency des Tokens
                    if token.dep_ in ["oa", "obj", "dobj"]:
                        priority = 0
                    else:
                        priority = 1

                    candidates.append((priority, phrase))

        # Sortiere und gebe den besten Treffer zurück
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]

        return ""