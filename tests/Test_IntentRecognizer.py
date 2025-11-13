import pytest

from src.nlp_assistant.pipelineParts.IntentRecognizer import IntentRecognizer


class TestIntentRecognizer:
    TEST_CASES = [
        # Leichtere Abfragen
        ("Schalte die Steckdose im Flur aus?", "turn_off"),
        ("Bitte die Lampe in der Küche anschalten.", "turn_on"),
        ("Wie warm ist es im Flur?", "get_value"),
        ("Heizung bitte auf 25 Grad stellen.", "set_value"),
        # Schwierigere Abfragen
        ("Die Lampe im Bad bitte aus machen.", "turn_off"),
        ("Die Beleuchtung im Flur aktivieren.", "turn_on"),
        ("Welchen Wert hat die Temperatur in der Küche?", "get_value"),
        ("Die Klimaanlage auf 20 Grad senken.", "set_value"),
    ]

    @pytest.mark.parametrize("command, expected_intent", TEST_CASES)
    def testIntentRecognizerPrediction(self, command: str, expected_intent: str):
        """
        Testet die Vorhersagefunktion des Intent Recognizers.
        Jedes Element in TEST_CASES wird dabei als separater Testfall ausgeführt.
        """

        # Testcases ausführen
        predicted_intent = IntentRecognizer.predictIntentFromCommand(command)

        # Gib eine Fehlermeldung bei falscher Vorhersage aus
        assert (predicted_intent == expected_intent), \
        f"FEHLER: Command:'{command}' Predicted: '{predicted_intent}' Korrekt: '{expected_intent}'"
