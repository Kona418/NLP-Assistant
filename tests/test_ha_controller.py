from unittest.mock import MagicMock

from src.nlp_assistant.backend.connection import HomeAssistantController, HomeAssistantRestManager


def test_init_loads_devices(real_device_list):
    # Arrange: Manager mocken und Rückgabewert setzen
    mock_manager = MagicMock(spec=HomeAssistantRestManager)
    mock_manager.get_device_list.return_value = real_device_list

    # Act
    controller = HomeAssistantController(mock_manager)

    # Assert
    mock_manager.get_device_list.assert_called_once()
    assert controller.device_list == real_device_list
    assert len(controller.device_list) > 0  # Prüft, ob die Liste nicht leer ist


def test_post_action_delegates(real_device_list):
    # Arrange
    mock_manager = MagicMock(spec=HomeAssistantRestManager)
    mock_manager.get_device_list.return_value = real_device_list
    controller = HomeAssistantController(mock_manager)

    action_request = {"domain": "light", "service": "turn_on", "name": "Deckenlampe"}

    # Act
    controller.post_action(action_request)

    # Assert: Prüfen, ob post_action, mit der gespeicherten Liste aufgerufen wurde
    mock_manager.post_action.assert_called_once_with(
        action_data=action_request,
        device_list=real_device_list
    )