import json
import os
import time

from dotenv import load_dotenv

from src.nlp_assistant.helper import HomeAssistantRestManager
from src.nlp_assistant.pipelineParts.IntentRecognizer import IntentRecognizer
from src.nlp_assistant.pipelineParts.HomeAssistantController import HomeAssistantController
from src.nlp_assistant.pipelineParts.deviceMatcher import DeviceMatcher


def main():
    start_time: time = time.time()

    current_time: time = time.time()
    print("start up")
    load_dotenv()
    user_input: str  = "Mach die Deckenlampe aus."
    ha_manager: HomeAssistantRestManager = HomeAssistantRestManager(ha_bearer_token=os.getenv("HA_TOKEN"), ha_base_url="http://homeassistant.local:8123")
    ha_controller: HomeAssistantController = HomeAssistantController(ha_manager=ha_manager)
    intent_recognizer: IntentRecognizer = IntentRecognizer()
    deviceMatcher: DeviceMatcher = DeviceMatcher()
    deviceList: list = ha_controller.get_device_list()
    intent_recognizer.load_model()
    print(time.time() - current_time)

    thinking_time: time = time.time()
    print("Thinking...")
    print("Finding Intent")
    intent: str = intent_recognizer.predict(user_input)[0]
    print(time.time() - current_time)
    print("Finding Device Name")
    current_time: time = time.time()
    raw_device_name: str = deviceMatcher.extractDeviceNamesFromCommands(user_input)
    device_name: dict = deviceMatcher.findBestDeviceMatch(targetDeviceName=raw_device_name, deviceList=deviceList)
    print(time.time() - current_time)
    action_input: dict = {
        "domain": f"{device_name["type"]}",
        "service": f"{intent}",
        "name": f"{device_name["name"]}"
    }
    ha_controller.post_action(action_input)
    print(time.time() - thinking_time)

    print(f"final time: {time.time()-start_time}")
if __name__ == '__main__':
    main()
