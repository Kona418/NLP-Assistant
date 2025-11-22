import csv
import os.path
from os.path import exists
from typing import Iterator

import numpy as np
import sklearn.model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class IntentRecognizer:

    def __init__(self):

        ...

    def _load_data_from_csv (self, csv_path: str = "data/trainingData/training_data.csv", delimiter: str =',') -> tuple[list[str], list[str]]:

        with open(csv_path, mode="r", encoding="utf-8") as training_data_file:

            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Training Data Not Found: {csv_path}")

            reader: Iterator[list[str]]= csv.reader(training_data_file, delimiter=delimiter)
            next(reader, None)

            data: list[str] = []
            label: list[str] = []
            data_tuple: tuple[list[str], list[str]] = (data, label)

            row: list
            for row in reader:
                if len(row) == 2:
                    text: str = row[0].strip()
                    intent: str = row[1].strip()

                    if text and intent:
                        data_tuple[0].append(text)
                        data_tuple[1].append(intent)

            return data_tuple


    def train_and_save(self, csv_path: str = "data/trainingData/training_data.csv", delimiter: str = ",", model_path: str = "src/nlp_assistant/data/models/intent_model.joblib", test_size: float = 0.1):
        print(f"~~~~~~ Start Training With: {csv_path} ~~~~~~")
        print(f"* Loading Data")

        data_tuple: tuple[list[str], list[str]] = self._load_data_from_csv(csv_path=csv_path, delimiter=delimiter)

        print(f"* Splitting Data")
        result: tuple = sklearn.model_selection.train_test_split(data_tuple[0], data_tuple[1], test_size=test_size, random_state=42, stratify=data_tuple[1])
        x_train_sub: list[str] = result[0]
        x_test_sub: list[str] = result[1]
        y_train_sub: list[str] = result[2]
        y_test_sub: list[str] = result[3]

        print(f"* Training Temporary Evaluation Model")

        # Vektorisierung für Evaluation initialisieren
        eval_vec: TfidfVectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)

        # Matrix erstellen (Typ ist scipy.sparse.csr_matrix, hier implizit gelassen oder 'Any')
        eval_matrix = eval_vec.fit_transform(x_train_sub)

        correct_predictions: int = 0

        # Typ-Hints für die Schleifen-Variablen (optional, aber passt zu deinem Style)
        text: str
        true_label: str

        for text, true_label in zip(x_test_sub, y_test_sub):
            # Einzelnen Satz transformieren
            vec = eval_vec.transform([text])
            # Ähnlichkeiten berechnen
            similarities = cosine_similarity(vec, eval_matrix)

            # Besten Index finden (numpy import benötigt)
            best_index: int = int(np.argmax(similarities))
            predicted_label: str = y_train_sub[best_index]
            score = similarities[0][best_index]

            if predicted_label == true_label:
                correct_predictions += 1
            else:
                print(f"Text: '{text}'")
                print(f"Erwartet: {true_label} | Vorhergesagt: {predicted_label} (Score: {score:.2f})")

        accuracy: float = correct_predictions / len(x_test_sub)

        print(f"--> Evaluation (Split {int(test_size * 100)}%): {len(x_train_sub)} Train, {len(x_test_sub)} Test")
        print(f"--> Model Accuracy: {accuracy:.2%}")
        ...

    def load_model(self, force_train: bool = False) -> bool:

        ...

    def predict(self, user_input: str) -> str | None:

        ...