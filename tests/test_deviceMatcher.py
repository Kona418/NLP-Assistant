import pytest

from src.nlp_assistant.backend.core.deviceMatcher import DeviceMatcher

class TestDeviceMatcher:
    TEST_CASES = [
        ("Schalte das Deckenlicht im Wohnzimmer ein", "Deckenlicht"),
        ("Mach die Standlampe im Schlafzimmer aus", "Standlampe"),
        ("Mach die TV-Steckdose im Wohnzimmer an", "TV-Steckdose"),
        ("Schalte die Playstation-Steckdose im Arbeitszimmer aus", "Playstation-Steckdose"),
    ]

    @pytest.mark.parametrize("command, expected_device", TEST_CASES)
    def testDeviceExtraction(self, command: str, expected_device: str) -> None:
        """
        Testet die Device-Extraktion aus Kommandos.
        Jedes Element in TEST_CASES wird als separater Testfall ausgeführt.
        """
        extracted_device = DeviceMatcher().extractDeviceNamesFromCommands(command)
        assert extracted_device == expected_device, \
            f"FEHLER: Command:'{command}' Extrahiertes Gerät: '{extracted_device}' Erwartet: '{expected_device}'"


    @pytest.fixture
    def device_list(self) -> list[dict]:
        # Beispiel-Geräteliste
        return [
            {"name": "Deckenlampe"},
            {"name": "Standlampe"},
            {"name": "Fernseher Steckdose"},
            {"name": "Playstation_Steckdose"}
        ]

    @pytest.mark.parametrize("target, expected_name", [
        ("Deckenlampe", "Deckenlampe"),
        ("Playstation", "Playstation_Steckdose"),
        ("Deckenleuchte", "Deckenlampe"),
        ("Fernseher", "Fernseher Steckdose"),
    ])
    def test_find_best_device_match(self, target: str, expected_name: str, device_list: list[dict])   -> None:
        matcher = DeviceMatcher()
        result = matcher.findBestDeviceMatch(target, device_list)
        assert result is not None, f"FEHLER: Kein Match gefunden für '{target}'"
        assert result['name'] == expected_name, \
            f"FEHLER: Target: '{target}' | Gefunden: '{result['name']}' | Erwartet: '{expected_name}'"
