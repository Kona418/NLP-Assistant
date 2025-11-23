import os
from dotenv import load_dotenv

from nlp_assistant.helper import HomeAssistantRestManager
from nlp_assistant.pipelineParts.IntentRecognizer import IntentRecognizer
from nlp_assistant.pipelineParts.HomeAssistantController import HomeAssistantController
from nlp_assistant.pipelineParts.deviceMatcher import DeviceMatcher

class backend:
    def __init__(self):
        print("--- Initializing Assistant Engine ---")

        load_dotenv()        
        token = os.getenv("HA_TOKEN")
        
        # Initialisierung
        self.ha_manager = HomeAssistantRestManager(
            ha_bearer_token=token, 
            ha_base_url="http://homeassistant.local:8123"
        )

        self.ha_controller = HomeAssistantController(ha_manager=self.ha_manager)
        
        self.intent_recognizer = IntentRecognizer(debug=True)
        # self.intent_recognizer.load_model()
    
        self.deviceMatcher = DeviceMatcher()
        self.deviceList = self.ha_controller.get_device_list()
        
        print("--- Initialization Complete ---")


    def process_command(self, user_input: str) -> dict:
        print(f"Processing command: {user_input}")

        print(1)
        intent = self.intent_recognizer.predict(user_input)[0]
        print(2)
        raw_device_name: str = self.deviceMatcher.extractDeviceNamesFromCommands(user_input)
        print(3)
        device_name: dict = self.deviceMatcher.findBestDeviceMatch(targetDeviceName=raw_device_name, deviceList=self.deviceList)
        print(4)
        action_input: dict = {
        "domain": f"{device_name["type"]}",
        "service": f"{intent}",
        "name": f"{device_name["name"]}"
        }

        self.ha_controller.post_action(action_input)

        return intent, raw_device_name, device_name, action_input