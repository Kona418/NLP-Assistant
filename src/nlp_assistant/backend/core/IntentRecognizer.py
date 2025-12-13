import csv
import os
import joblib
import numpy as np
import spacy
import sklearn.model_selection
from typing import Iterator, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Globaler NLP-Cache für die Tokenizer-Funktion (notwendig für joblib pickling)
_nlp_model = None


def _global_spacy_tokenizer(text: str) -> list[str]:
    """
    Standalone tokenizer function to allow pickling of the TfidfVectorizer.
    """
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("de_core_news_sm")
        except OSError:
            from spacy.cli import download
            download("de_core_news_sm")
            _nlp_model = spacy.load("de_core_news_sm")

    doc = _nlp_model(text)
    tokens: list[str] = []

    # Relevant POS tags for intent (verbs, adverbs, particles)
    intent_relevant_pos = {'CCONJ', 'VERB', 'ADP', 'PROPN', 'AUX'}

    for token in doc:
        if token.pos_ in intent_relevant_pos:
            tokens.append(token.lemma_.lower())
    return tokens


class IntentRecognizer:
    """
    Intent recognition using TF-IDF and Cosine Similarity.
    """

    def __init__(self, model_path: str = os.path.join('src', 'nlp_assistant', 'data', 'models', 'intent_model.joblib'),
                 debug: bool = False,
                 force_train: bool = False):
        """
        Initializes the recognizer.

        Args:
            model_path (str): Path to save/load the trained model.
            debug (bool): If True, enables print statements.
            force_train (bool): If True, prevents loading an existing model to enforce retraining.
        """
        self.model_path: str = model_path
        self.threshold: float = 0.4
        self.debug: bool = debug
        self.force_train: bool = force_train

        # --- Configure Vectorizer ---
        # Note: Uses global tokenizer function to support joblib serialization
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(
            tokenizer=_global_spacy_tokenizer,
            token_pattern=None,
            ngram_range=(1, 2),
            lowercase=True,
            use_idf=True,
            sublinear_tf=True
        )

        self.training_labels: list[str] = []
        self.tfidf_matrix = None
        self.is_trained: bool = False

        # Initial load attempt
        self.load_model()

    def _load_data_from_csv(self, csv_path: str, delimiter: str = ',') -> tuple[list[str], list[str]]:
        """
        Loads training data from a CSV file.

        Args:
            csv_path (str): Path to the CSV file.
            delimiter (str): CSV delimiter character.

        Returns:
            tuple: A tuple containing a list of sentences and a list of labels.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Training Data Not Found: {csv_path}")

        with open(csv_path, mode="r", encoding="utf-8") as training_data_file:
            reader: Iterator[list[str]] = csv.reader(training_data_file, delimiter=delimiter)
            next(reader, None)

            data: list[str] = []
            label: list[str] = []

            for row in reader:
                if len(row) >= 2:
                    text: str = row[0].strip()
                    intent: str = row[1].strip()

                    if text and intent:
                        data.append(text)
                        label.append(intent)

            return data, label

    def _save_to_disk(self):
        """
        Saves the current model state to disk.
        """
        if self.debug:
            print(f"* Saving Model to {self.model_path}")

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        data = {
            "vectorizer": self.vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "labels": self.training_labels,
            "threshold": self.threshold
        }
        joblib.dump(data, self.model_path)

        if self.debug:
            print(f"--> Model Saved Successfully")

    def train_and_save(self, csv_path: str = os.path.join('src', 'nlp_assistant', 'data', 'trainingData',
                                                          'training_data.csv'), delimiter: str = ",",
                       test_size: float = 0.2):
        """
        Trains the model on a split, evaluates it, and saves the result.

        Args:
            csv_path (str): Path to training data.
            delimiter (str): CSV delimiter.
            test_size (float): Percentage of data used for evaluation (0.0-1.0).
        """

        if self.debug:
            print(f"~~~~~~ Start Training With: {csv_path} ~~~~~~")
            print(f"* Loading Data")

        data_tuple: tuple[list[str], list[str]] = self._load_data_from_csv(csv_path=csv_path, delimiter=delimiter)

        if not data_tuple[0]:
            raise ValueError("CSV is empty.")

        # --- Data Splitting ---
        if self.debug:
            print(f"* Splitting Data (Test Size: {test_size})")

        try:
            result: tuple = sklearn.model_selection.train_test_split(
                data_tuple[0],
                data_tuple[1],
                test_size=test_size,
                random_state=42,
                stratify=data_tuple[1]
            )
        except ValueError:
            result: tuple = sklearn.model_selection.train_test_split(
                data_tuple[0],
                data_tuple[1],
                test_size=test_size,
                random_state=42
            )

        x_train_sub: list[str] = result[0]
        x_test_sub: list[str] = result[1]
        y_train_sub: list[str] = result[2]
        y_test_sub: list[str] = result[3]

        # --- Training ---
        if self.debug:
            print(f"* Training Model on Training Split ({len(x_train_sub)} items)")

        # Fit vectorizer only on training data
        self.tfidf_matrix = self.vectorizer.fit_transform(x_train_sub)
        self.training_labels = y_train_sub
        self.is_trained = True

        # --- Evaluation ---
        if self.debug:
            print(f"* Evaluating on Test Split ({len(x_test_sub)} items)")

        correct_predictions: int = 0
        text: str
        true_label: str

        for text, true_label in zip(x_test_sub, y_test_sub):
            vec = self.vectorizer.transform([text])
            similarities = cosine_similarity(vec, self.tfidf_matrix)

            best_index: int = int(np.argmax(similarities))
            predicted_label: str = self.training_labels[best_index]
            score: float = similarities[0][best_index]

            if predicted_label == true_label:
                correct_predictions += 1
            else:
                if self.debug:
                    print(f"  [MISS] '{text}' -> Pred: {predicted_label} ({score:.2f}) | True: {true_label}")

        accuracy: float = correct_predictions / len(x_test_sub) if len(x_test_sub) > 0 else 0.0

        if self.debug:
            print(f"--> Evaluation Results: {len(x_train_sub)} Train, {len(x_test_sub)} Test")
            print(f"--> Saved Model Accuracy: {accuracy:.2%}")

        # --- Save ---
        self._save_to_disk()

    def load_model(self) -> bool:
        """
        Loads the model from the file system.

        Returns:
            bool: True if model is ready (loaded or trained), False if loading/training failed.
        """
        # Case 1: Force train or file missing -> Train
        if self.force_train or not os.path.exists(self.model_path):
            if self.debug and self.force_train:
                print("! Force train enabled. Triggering training...")

            try:
                self.train_and_save()
                return True  # Successfully trained
            except Exception as e:
                if self.debug:
                    print(f"Error during enforced training: {e}")
                return False

        # Case 2: Load existing model
        try:
            data = joblib.load(self.model_path)
            self.vectorizer = data["vectorizer"]
            self.tfidf_matrix = data["tfidf_matrix"]
            self.training_labels = data["labels"]
            self.threshold = data.get("threshold", 0.4)
            self.is_trained = True
            return True
        except Exception as e:
            if self.debug:
                print(f"Error loading model: {e}")
                print("! Attempting to retrain due to load error...")

            # Fallback: Retrain if load fails
            try:
                self.train_and_save()
                return True
            except Exception as train_e:
                if self.debug:
                    print(f"Retraining failed: {train_e}")
                return False

    def predict(self, user_input: str) -> tuple[Optional[str], float]:
        """
        Predicts the intent for a given input string.

        Args:
            user_input (str): The user's command.

        Returns:
            tuple[Optional[str], float]: The predicted intent (or None) and the confidence score.
        """
        if not self.is_trained:
            if not self.load_model():
                raise RuntimeError("Model is not trained and no file found.")

        user_vec = self.vectorizer.transform([user_input])
        similarities = cosine_similarity(user_vec, self.tfidf_matrix)

        best_index: int = int(np.argmax(similarities))
        best_score: float = similarities[0][best_index]

        if best_score < self.threshold:
            return None, best_score

        return self.training_labels[best_index], best_score


if __name__ == "__main__":
    print("~~~~~~~ Start IntentRecognizer Direct Execution ~~~~~~~")

    recognizer = IntentRecognizer(debug=True, force_train=True)

    test_phrase = "mach die Deckenlampe an."
    print(f"\nTest Prediction for: '{test_phrase}'")
    intent, confidence = recognizer.predict(test_phrase)
    print(f"Result -> Intent: {intent}, Confidence: {confidence:.2f}")