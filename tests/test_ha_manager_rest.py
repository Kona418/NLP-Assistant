import pytest
from unittest.mock import patch

from src.nlp_assistant.backend.connection import HomeAssistantRestManager


@pytest.fixture
def manager():
    return HomeAssistantRestManager("http://mock-ha:8123", "mock-token")


def test_resolve_name_to_entity_id(manager, real_device_list):
    """Testet die Auflösung von 'Deckenlampe' -> 'light.deckenlampe'"""

    # Input: Name statt ID
    action_input = {
        "domain": "light",
        "service": "turn_on",
        "name": "Deckenlampe"  # Dieser Name steht in deiner JSON
    }

    # Wir fangen den HTTP Request ab
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        # Act
        manager.post_action(action_input, real_device_list)

        # Assert
        # Wir holen uns die Daten, die an requests.post übergeben wurden
        call_args = mock_post.call_args
        sent_payload = call_args[1]['json']

        # Wichtigste Prüfung: Wurde der Name durch die ID ersetzt?
        assert sent_payload["entity_id"] == "light.deckenlampe"
        assert "name" not in sent_payload


def test_resolve_switch_name(manager, real_device_list):
    """Testet Auflösung eines Switches aus deiner Liste"""
    action_input = {
        "domain": "switch",
        "service": "turn_off",
        "name": "TV Steckdose Steckdose 1"
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        manager.post_action(action_input, real_device_list)

        sent_payload = mock_post.call_args[1]['json']
        assert sent_payload["entity_id"] == "switch.tv_steckdose_steckdose_1"


def test_unknown_device_returns_none(manager, real_device_list):
    """Testet Verhalten bei unbekanntem Gerät"""
    action_input = {
        "domain": "light",
        "service": "turn_on",
        "name": "Nicht existierende Lampe"
    }

    # Act
    result = manager.post_action(action_input, real_device_list)

    # Assert
    assert result is None