import spacy


class DeviceMatcher:

    def __init__(self, SIMILARITY_THRESHOLD=0.5) -> None:
        
        self.SIMILARITY_THRESHOLD = SIMILARITY_THRESHOLD

        try:
            self.nlp = spacy.load("de_core_news_lg")
        except OSError:
            from spacy.cli import download
            download("de_core_news_lg")
            self.nlp= spacy.load("de_core_news_lg")
        

    def findBestDeviceMatch(self, targetDeviceName: str, deviceList: list) -> dict | None:
        """
        Findet das beste passende Gerät aus der Geräteliste basierend auf dem Gerätenamen.

        Args:
            device_name (str): Name des Geräts, das abgeglichen werden soll.
            deviceList (list): Liste der verfügbaren Geräte.

        Returns:
            dict | None: Das beste passende Gerät oder None, wenn kein passendes Gerät gefunden wurde.
        """
        targetDeviceName_doc: spacy.tokens.Doc = self.nlp(targetDeviceName.lower())
        best_match: dict | None = None
        highest_similarity: float = 0.0

        for device in deviceList:
            device_doc: spacy.tokens.Doc = self.nlp(device['name'].lower())
            similarity: float = targetDeviceName_doc.similarity(device_doc)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = device

        # Überprüfung, ob die höchste Ähnlichkeit über dem Schwellenwert liegt
        if highest_similarity >= self.SIMILARITY_THRESHOLD:
            print(f"Bestes Match für: '{targetDeviceName}' =  '{best_match['name']}' mit Ähnlichkeit {highest_similarity:.2f}")
            return best_match
        else:
            print(f"Es wurde kein Match für das Gerät '{targetDeviceName}' gefunden.")
            return None
            

    def extractDeviceNamesFromCommands(self, command: str) -> str:
        """
        Extrahiert den DeviceName aus dem Sprachbefehl.

        Args:
            command (str): Der Sprachbefehl.
        
        Returns:
            str: Der extrahierte DeviceName.
        """
        doc = self.nlp(command)
      
        for token in doc:
            # 1. Direktes Device über relevante Dependencies
            if token.dep_ in ["oa", "sb", "obj", "dobj", "pd"] and token.pos_ in ["NOUN", "PROPN"]:
                return token.text

            # 2. Device als Head eines ag-Attributes
            if token.dep_ == "ag" and token.head.pos_ in ["NOUN", "PROPN"]:
                return token.head.text
            
            # 3. Fallback: NOUN/PROPN, der/das/die vorhergehendem Verb folgt
            if token.pos_ in ["NOUN", "PROPN"] and token.i > 0:
                prev = doc[token.i - 1]
                if prev.pos_ == "DET" or prev.pos_ == "VERB" or prev.dep_ in ["ROOT"]:
                    return token.text

        print("Kein Device gefunden.")
        return ""