import joblib
import pandas as pd
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline


class IntentRecognizer:

    MODEL_PATH = "src/nlp_assistant/data/models/intent_model.joblib"

    def trainIntentRecognizerModel(training_data:pd.DataFrame): 
        """
        Transformiert die Trainingsdaten in einen Vektor, trainiert einen Support Vector Classifier 
        und speichert das trainierte Modell anschließend als Joblib-Datei.
        
        Args:
            training_data (pd.DataFrame): DataFrame mit den Trainingsdaten, die die Spalten "Command" und "Intent" enthalten.
            
        """
        sentences = training_data["Command"]
        labels = training_data["Intent"] 
        
        # Pipeline erstellen: Vektorisierung + Klassifikation
        model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), SVC(kernel='linear')) 
        model.fit(sentences, labels)

        # Modell speichern
        joblib.dump(model, IntentRecognizer.MODEL_PATH)

        print("Intent Recognizer Model erfolgreich auf den Testdaten trainiert und gespeichert.")


    def predictIntentFromCommand(text:str) -> str:
        """
        Gibt eine Vorhersage für die Absicht (Intent) für den gegebenen Text zurück.

        Args:
            text (str): Der Eingabetext, für den die Absicht vorhergesagt werden soll.
        Returns:
            str: Die vorhergesagte Absicht (Intent) des Eingabetextes.
        """

        # Modell laden und Vorhersage treffen
        model = joblib.load(IntentRecognizer.MODEL_PATH)
        
        prediction = model.predict([text])[0]
        return prediction