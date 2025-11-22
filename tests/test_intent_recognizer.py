import pytest
import numpy as np
import os
from unittest.mock import patch, MagicMock, mock_open

# Import module
from src.nlp_assistant.pipelineParts.TempIntentRecognizer import IntentRecognizer


@pytest.fixture
def recognizer():
    """
    Fixture: Creates an instance with a dummy path and debug mode disabled.
    """
    # Use path with folder structure to satisfy os.path.dirname calls
    return IntentRecognizer(model_path="data/models/dummy_model.pkl", debug=False)


def test_tokenizer_filters_nouns(recognizer):
    """
    Tests if the tokenizer correctly filters nouns/articles and keeps verbs/particles.
    """
    # --- Arrange ---
    # Use a sentence with clear grammatical structure
    text = "Ich aktiviere das Licht in der Küche sofort"

    # --- Act ---
    tokens = recognizer._spacy_tokenizer(text)

    # --- Assert ---
    # Verbs must be preserved (lemmatized)
    assert "aktivieren" in tokens
    # Nouns must be removed
    assert "licht" not in tokens
    assert "küche" not in tokens
    # Articles must be removed
    assert "das" not in tokens


def test_predict_returns_intent_above_threshold(recognizer):
    """
    Tests if predict returns the correct intent when score > threshold.
    """
    # --- Arrange ---
    recognizer.is_trained = True
    recognizer.threshold = 0.5
    recognizer.training_labels = ["turn_on", "turn_off"]

    # Mock internal vectorizer
    mock_vec = MagicMock()
    mock_vec.transform.return_value = "mock_vector"
    recognizer.vectorizer = mock_vec

    # --- Act ---
    # Patch cosine_similarity in the source module
    with patch("src.nlp_assistant.pipelineParts.TempIntentRecognizer.cosine_similarity") as mock_sim:
        mock_sim.return_value = np.array([[0.9, 0.1]])
        intent, score = recognizer.predict("Licht an")

    # --- Assert ---
    assert intent == "turn_on"
    assert score == 0.9


def test_predict_returns_none_below_threshold(recognizer):
    """
    Tests if predict returns None when score < threshold.
    """
    # --- Arrange ---
    recognizer.is_trained = True
    recognizer.threshold = 0.95
    recognizer.training_labels = ["turn_on", "turn_off"]

    mock_vec = MagicMock()
    recognizer.vectorizer = mock_vec

    # --- Act ---
    with patch("src.nlp_assistant.pipelineParts.TempIntentRecognizer.cosine_similarity") as mock_sim:
        # Score (0.5) is lower than threshold (0.95)
        mock_sim.return_value = np.array([[0.5, 0.1]])
        intent, score = recognizer.predict("Unsinn")

    # --- Assert ---
    assert intent is None
    assert score == 0.5


def test_train_and_save_process(recognizer):
    """
    Tests the complete training pipeline including file I/O mocking.
    """
    # --- Arrange ---
    csv_content = "sentence,intent\nLicht an,turn_on\nLicht aus,turn_off"

    # Mock all filesystem and external dependencies
    with patch("builtins.open", mock_open(read_data=csv_content)), \
            patch("os.path.exists", return_value=True), \
            patch("os.makedirs") as mock_mkdirs, \
            patch("joblib.dump") as mock_dump, \
            patch("sklearn.model_selection.train_test_split") as mock_split:
        # Define split return values
        mock_split.return_value = (["Licht an"], ["Licht aus"], ["turn_on"], ["turn_off"])

        # --- Act ---
        recognizer.train_and_save("dummy.csv")

        # --- Assert ---
        assert recognizer.is_trained is True
        # Check if model save was triggered
        mock_dump.assert_called_once()
        # Check if directory creation was attempted
        mock_mkdirs.assert_called()


def test_load_model_fails_gracefully(recognizer):
    """
    Tests behavior when the model file does not exist.
    """
    # --- Act ---
    with patch("os.path.exists", return_value=False):
        result = recognizer.load_model()

    # --- Assert ---
    assert result is False
    assert recognizer.is_trained is False


def test_load_model_respects_force_train():
    """
    Tests if load_model returns False when force_train is set,
    even if the file exists.
    """
    # --- Arrange ---
    # Create recognizer with force_train=True
    recognizer_forced = IntentRecognizer(model_path="data/models/dummy_model.pkl", debug=False, force_train=True)

    # --- Act ---
    # Simulate that the file exists
    with patch("os.path.exists", return_value=True):
        result = recognizer_forced.load_model()

    # --- Assert ---
    # Should return False because force_train is on
    assert result is False
    assert recognizer_forced.is_trained is False