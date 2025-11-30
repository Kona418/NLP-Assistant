import os
import random

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

        match intent:
            case "turn_on":
                execution_data = ha_command(self, intent=intent, user_input=user_input)

                anschalten = [
                    f"Schalte {execution_data[2].get('name')} an.",
                    f"Schalte {execution_data[2].get('name')} ein.",
                    f"Aktiviere {execution_data[2].get('name')}.",
                    f"Mache {execution_data[2].get('name')} an.",
                    f"Starte {execution_data[2].get('name')}."
                ]

                output_string: str = random.choice(anschalten)

                print(output_string)

                return execution_data

            case "turn_off":
                execution_data = ha_command(self, intent=intent, user_input=user_input)

                ausschalten = [
                    f"Schalte {execution_data[2].get('name')} aus.",
                    f"Deaktiviere {execution_data[2].get('name')}.",
                    f"Mache {execution_data[2].get('name')} aus.",
                    f"Schalte {execution_data[2].get('name')} ab.",
                    f"Stoppe {execution_data[2].get('name')}."
                ]

                output_string: str = random.choice(ausschalten)

                print(output_string)

                return execution_data

            case "toggle":
                execution_data = ha_command(self, intent=intent, user_input=user_input)

                umschalten = [
                    f"Schalte {execution_data[2].get('name')} um.",
                    f"Wechsle den Status von {execution_data[2].get('name')}.",
                    f"Ändere den Zustand von {execution_data[2].get('name')}.",
                    f"Invertiere {execution_data[2].get('name')}.",
                    f"Betätige den Schalter für {execution_data[2].get('name')}."
                ]

                output_string: str = random.choice(umschalten)

                print(output_string)

                return execution_data

            case _:
                print("Unknown Intent")

def ha_command(self, user_input: str, intent: str) -> dict:
    # Extraktion des DeviceName und Abgleich mit der Geräteliste des HomeAssistant
    raw_device_name: str = self.deviceMatcher.extractDeviceNamesFromCommands(user_input)
    device_name: dict = self.deviceMatcher.findBestDeviceMatch(targetDeviceName=raw_device_name,
                                                               deviceList=self.deviceList)

    # Aktion erstellen und an HomeAssistant senden
    action_input: dict = {
        "domain": f"{device_name["type"]}",
        "service": f"{intent}",
        "name": f"{device_name["name"]}"
    }

    # Aktion an HomeAssistant senden
    self.ha_controller.post_action(action_input)

    return intent, raw_device_name, device_name, action_input