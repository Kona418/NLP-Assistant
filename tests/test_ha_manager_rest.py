import pytest

from nlp_assistant.helper.HomeAssistentRestManager import getDeviceList, postAction

TEST_LIGHT_NAME = "Deckenlampe"
TEST_SWITCH_ID = "switch.tv_steckdose_steckdose_1"

@pytest.fixture(scope="module")
def device_list():

    print("Frage Geräteliste von HA ab")
    list_data = getDeviceList()
    assert list_data is not None, "getDeviceList failed, ist der HA-Server erreichbar?"
    return list_data


def test_getDeviceList_fetches_data(device_list):
    assert isinstance(device_list, list)
    assert len(device_list) > 0, "Findet keine light oder switch Geräte. Vielleicht gibt es keine in HA?"

def test_getDeviceList_structure(device_list):
    device = device_list[0]

    assert "name" in device
    assert "entity_id" in device
    assert "type" in device
    assert "actions" in device
    assert "capabilities" in device
    assert device.get("type") in ["light", "switch"]

# @pytest.mark.skip(reason="Steuert echte Geräte")
def test_postAction_by_name(device_list):

    print(f"TEST: Schalte '{TEST_LIGHT_NAME}' an")
    action = {
        "domain": "light",
        "service": "turn_on",
        "name": TEST_LIGHT_NAME,
        "brightness_pct": 50
    }

    response = postAction(action, device_list)

    assert response is not None, "postAction failed"
    assert isinstance(response, list)

# @pytest.mark.skip(reason="Steuert echte Geräte")
def test_postAction_by_id(device_list):

    print(f"TEST: Schalte '{TEST_SWITCH_ID}' an")
    action = {
        "domain": "switch",
        "service": "turn_on",
        "entity_id": TEST_SWITCH_ID
    }

    response = postAction(action, device_list)

    assert response is not None, "postAction failed"
    assert isinstance(response, list)