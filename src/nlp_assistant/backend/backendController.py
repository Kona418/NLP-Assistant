import os
from dotenv import load_dotenv

from nlp_assistant.backend.connection.HomeAssistantController import HomeAssistantController
from nlp_assistant.backend.connection.HomeAssistantRestManager import HomeAssistantRestManager
from nlp_assistant.backend.core.IntentRecognizer import IntentRecognizer
from nlp_assistant.backend.core.deviceMatcher import DeviceMatcher


class backendController:
    def __init__(self)  -> None:
        print("--- Initialization ... ---")

        # Laden der Umgebungsvariablen
        load_dotenv()        
        token = os.getenv("HA_TOKEN")
        
        # Initialisierung der HomeAssistant Verbindung
        self.ha_manager = HomeAssistantRestManager(
            ha_bearer_token=token, 
            ha_base_url="http://homeassistant.local:8123"
        )

        # Initialisierung des HomeAssistant Controllers
        self.ha_controller = HomeAssistantController(ha_manager=self.ha_manager)
        
        # Initialisierung des Intent Recognizers
        self.intent_recognizer = IntentRecognizer()
    
        # Initialisierung des Device Matchers
        self.deviceMatcher = DeviceMatcher()
        self.deviceList = self.ha_controller.get_device_list()

        with open("src/nlp_assistant/data/deviceList.json", "r", encoding="utf-8") as f:
            import json
            self.deviceList = json.load(f)

        print("--- Initialization complete! ---")


    def process_command(self, user_input: str) -> dict:
        print(f"Processing command: {user_input}")

        # Intent Erkennung
        intent = self.intent_recognizer.predict(user_input)[0]
        
        # Extraktion des DeviceName und Abgleich mit der Geräteliste des HomeAssistant
        raw_device_name: str = self.deviceMatcher.extractDeviceNamesFromCommands(user_input)
        device_name: dict = self.deviceMatcher.findBestDeviceMatch(targetDeviceName=raw_device_name, deviceList=self.deviceList)

        # Aktion erstellen und an HomeAssistant senden
        action_input: dict = {
        "domain": f"{device_name["type"]}",
        "service": f"{intent}",
        "name": f"{device_name["name"]}"
        }

        # Aktion an HomeAssistant senden
        self.ha_controller.post_action(action_input)

        return intent, raw_device_name, device_name, action_input